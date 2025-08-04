import enum
import warnings
from datetime import date, datetime
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Type, Union, get_args
from uuid import UUID

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import (
    ArrayField,
    BigIntegerRangeField,
    DateRangeField,
    IntegerRangeField,
)
from django.db.models import CharField
from django.db.models import Model as DjangoModel
from django.db.models.fields import Field as DjangoField
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from ninja.orm.fields import TYPES as BASE_TYPES
from ninja.orm.fields import AnyObject, title_if_lower
from pydantic import UUID4, AliasChoices
from pydantic import BaseModel as PydanticBaseModel
from pydantic import constr
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined  # type: ignore
from typing_extensions import TypeAliasType

from pop.core.measures import Measure
from pop.core.measures.fields import MeasurementField
from pop.core.schemas import CodedConcept as CodedConceptSchema
from pop.core.schemas import Period as PeriodSchema
from pop.core.schemas import Range as RangeSchema
from pop.core.serialization import filters as schema_filters
from pop.core.types import Array, Nullable, Username
from pop.core.utils import (
    camel_to_snake,
    is_enum,
    is_list,
    is_literal,
    is_optional,
    is_union,
    to_camel_case,
)
from pop.terminology.models import CodedConcept as CodedConceptModel

UserModel = get_user_model()

DJANGO_TO_PYDANTIC_TYPES = {
    **BASE_TYPES,
}


class SchemaFieldInfo:
    """
    Holds metadata and configuration for a schema field used in serialization.

    Attributes:
        resolver_fcn (Callable[..., Any] | None): Optional function to resolve or transform the field value.
        python_type (Any): The expected Python type of the field.
        serialization_alias (str): The name to use for this field during serialization.
        default (Any): The default value for the field if not provided.
        default_factory (Callable[[], Any] | None): Optional factory function to generate a default value.
        extras (Dict[str, Any]): Additional metadata or options for the field.
    """

    def __init__(
        self,
        resolver_fcn: Callable[..., Any] | None,
        python_type: Any,
        serialization_alias: str,
        default: Any,
        default_factory: Callable[[], Any] | None,
        extras: Dict[str, Any],
    ):
        self.resolver_fcn = resolver_fcn
        self.python_type = python_type
        self.serialization_alias = serialization_alias
        self.default = default
        self.default_factory = default_factory
        self.extras = extras


class SchemaFieldDefinition:
    """
    Represents a field definition in a schema, including its type, alias, and additional metadata.

    Attributes:
        name (str): The name of the field.
        python_type (Any): The Python type of the field.
        field_info (FieldInfo): Pydantic FieldInfo object containing metadata for the field.
        resolver_fcn (Callable[..., Any] | None): Optional function to resolve or transform the field value.
    """

    def __init__(
        self,
        name: str,
        python_type: Any,
        field_info: FieldInfo,
        resolver_fcn: Callable[..., Any] | None = None,
    ):
        self.name = name
        self.resolver_fcn = resolver_fcn
        self.python_type = python_type
        self.field_info = field_info


def get_schema_field(
    field: DjangoField,
    *,
    expand: str | None = None,
    optional: bool = False,
    exclude_related_fields: List[str] | None = None,
) -> "SchemaFieldDefinition":
    """
    Generates a schema field definition from a Django model field.

    Handles both relation and non-relation fields, including support for array fields.
    Optionally expands related fields and marks fields as optional or nullable based on
    field attributes or explicit parameters.

    Args:
        field (DjangoField): The Django model field to convert.
        expand (str | None, optional): Name of the related field to expand, if any.
        optional (bool, optional): Whether the field should be considered optional.
        exclude_related_fields (List[str] | None, optional): List of related field names to exclude from expansion.

    Returns:
        SchemaFieldDefinition: The generated schema field definition with type, alias, and resolver.
    """
    is_array_field = isinstance(field, ArrayField)
    if is_array_field:
        field = field.base_field
    if field.is_relation:
        info = process_relation_field(field, exclude_related_fields, expand)
    else:
        info = process_non_relation_field(field)
    if is_array_field:
        info.python_type = List[info.python_type]
    info.extras.update({"x-expanded": expand})
    field_info = create_field_info(
        field,
        info.serialization_alias,
        default=info.default,
        default_factory=info.default_factory,
        optional=optional,
        **info.extras,
    )
    # Determine nullability based on field options or explicit optional parameter
    is_nullable = (
        getattr(field, "null", False) or getattr(field, "blank", False) or optional
    )
    if is_nullable:
        info.python_type = Nullable[info.python_type]
    return SchemaFieldDefinition(
        info.serialization_alias,
        info.python_type,
        field_info,
        info.resolver_fcn,
    )


def process_non_relation_field(
    field: DjangoField,
) -> "SchemaFieldInfo":
    """
    Processes a non-relation Django model field and returns a SchemaFieldInfo object
    containing metadata for serialization.

    This function determines the appropriate Python type, serialization alias,
    default value or factory, and any extra metadata required for the field.
    It handles special cases for custom fields such as MeasurementField, DateRangeField,
    IntegerRangeField, BigIntegerRangeField, and CharField with choices (enums).
    For other field types, it falls back to a mapping from Django internal types
    to Pydantic types.

    Args:
        field (DjangoField): The Django model field to process.

    Returns:
        SchemaFieldInfo: An object containing information about the field for schema
        generation and serialization.
    """
    from .base import BaseSchema

    extras: Dict[str, Any] = {}
    resolver_fcn: Optional[Callable[..., Any]] = None
    serialization_alias: str = to_camel_case(field.name)
    internal_type: str = field.get_internal_type()

    # Handle MeasurementField
    if isinstance(field, MeasurementField):
        python_type = Measure
        resolver_fcn = partial(BaseSchema._resolve_measure, orm_field_name=field.name)
        extras["x-measure"] = field.measurement.__name__
        default_unit = field.get_default_unit()
        if default_unit is not None:
            extras["x-default-unit"] = default_unit.replace("__", "/")

    # Handle DateRangeField
    elif isinstance(field, DateRangeField):
        python_type = PeriodSchema

    # Handle Integer/BigInteger Range Fields
    elif isinstance(field, (BigIntegerRangeField, IntegerRangeField)):
        python_type = RangeSchema

    # Handle CharField with choices (enums)
    elif isinstance(field, CharField) and field.choices is not None:
        choices = field.choices() if callable(field.choices) else field.choices
        enum_name = (
            f"{field.model.__name__ if hasattr(field, 'model') else ''}"
            f"{to_camel_case(field.name)[0].upper() + to_camel_case(field.name)[1:]}Choices"
        )
        python_type = enum.Enum(
            enum_name,
            {str(value).upper(): value for value, _ in choices},
            type=str,
        )

    # Fallback to DJANGO_TO_PYDANTIC_TYPES or str
    else:
        python_type = DJANGO_TO_PYDANTIC_TYPES.get(internal_type, str)

    # Handle default values and default factories
    default: Any = PydanticUndefined
    default_factory: Optional[Callable[[], Any]] = None
    if field.has_default() and not field.primary_key:
        if callable(field.default):
            default = PydanticUndefined
            try:
                # Check if the default callable can be called without arguments
                field.default()
                default_factory = lambda: field.default()
            except TypeError:
                # If not, skip using as default_factory
                default_factory = None
        else:
            default = field.default
            default_factory = None
    else:
        default, default_factory = PydanticUndefined, None

    return SchemaFieldInfo(
        resolver_fcn,
        python_type,
        serialization_alias,
        default,
        default_factory,
        extras,
    )


def process_relation_field(
    field: DjangoField,
    exclude_related_fields: List[str] | None = None,
    expand: str | None = None,
) -> "SchemaFieldInfo":
    """
    Processes a Django model relation field and returns a SchemaFieldInfo object describing
    how the field should be serialized for API schemas.

    Depending on the `expand` parameter, the function either expands the related model
    into a nested schema or represents the relation as a reference (e.g., an ID or list of IDs).
    Handles both single and multiple relations (ForeignKey, OneToOne, ManyToMany, etc.).

    Args:
        field: The Django model relation field to process.
        exclude_related_fields (List[str] | None): Optional list of related model field names to exclude from the schema.
        expand (str | None): If provided, expands the related model using the given schema name; otherwise, uses a reference.

    Returns:
        SchemaFieldInfo: An object containing information about how to serialize the relation field,
        including the resolver function, Python type, serialization alias, default values, and any extra metadata.
    """
    from .base import BaseSchema
    from .factory import create_schema

    is_many_related = field.one_to_many or field.many_to_many
    serialization_alias = to_camel_case(field.name)
    if not field.related_model:
        raise ValueError(f"Field '{field.name}' has no related model defined.")
    related_model = field.related_model
    extras = {}

    if expand:
        # If expand is set, use the related model's schema for full expansion
        related_schema = create_schema(
            related_model, exclude=exclude_related_fields, name=expand
        )
        resolver_fcn = partial(
            (
                BaseSchema._resolve_expanded_many_to_many
                if is_many_related
                else BaseSchema._resolve_expanded_foreign_key
            ),
            orm_field_name=field.name,
            related_schema=related_schema,
        )
        python_type = List[related_schema] if is_many_related else related_schema
    else:
        # Otherwise, use a reference (id or ids) to the related model
        resolver_fcn, related_type, serialization_alias, extras = (
            get_related_field_type(field, related_model, serialization_alias)
        )
        python_type = List[related_type] if is_many_related else related_type

    # Determine if the relation is optional (nullable, blank, or auto-created reverse relation)
    optional = (
        (getattr(field, "concrete", False) and field.auto_created)
        or field.null
        or field.blank
    )

    # Set default and default_factory based on relation type and optionality
    if is_many_related:
        default = []
        default_factory = list
    else:
        default = None if optional else PydanticUndefined
        default_factory = None

    return SchemaFieldInfo(
        resolver_fcn,
        python_type,
        serialization_alias,
        default,
        default_factory,
        extras,
    )


def get_related_field_type(
    field: DjangoField, related_model: type[DjangoModel], serialization_alias: str
) -> tuple[Callable | None, Any, str, Dict[str, Any]]:
    """
    Determines the serialization type and resolver for a Django related field.

    Args:
        field (DjangoField): The Django model field representing the relation.
        related_model (type[DjangoModel]): The related Django model class.
        serialization_alias (str): The base alias to use for serialization.

    Returns:
        tuple:
            - Callable | None: A resolver function for the related field, or None if not needed.
            - Any: The type to use for serialization (e.g., a schema class or primitive type).
            - str: The serialization alias, possibly modified (e.g., with "Id" or "Ids" suffix).
            - Dict[str, Any]: Additional metadata or extras for serialization.

    Notes:
        - Handles special cases for models inheriting from `CodedConceptModel` and `UserModel`.
        - For other models, determines the appropriate resolver and type based on the field's relation type.
    """
    from .base import BaseSchema

    if issubclass(related_model, CodedConceptModel):
        extras = {"x-terminology": related_model.__name__}
        return None, CodedConceptSchema, serialization_alias, extras
    if issubclass(related_model, UserModel):
        return (
            partial(
                BaseSchema._resolve_user,
                orm_field_name=field.name,
                many=field.many_to_many or False,
            ),
            Union[Username, str],
            serialization_alias,
            {},
        )

    resolver_fcn = partial(
        (
            BaseSchema._resolve_many_to_many
            if field.many_to_many
            else BaseSchema._resolve_foreign_key
        ),
        orm_field_name=field.name,
    )
    internal_type = related_model._meta.get_field("id").get_internal_type()
    related_type = DJANGO_TO_PYDANTIC_TYPES.get(internal_type, int)
    serialization_alias += "Ids" if field.many_to_many else "Id"

    return resolver_fcn, related_type, serialization_alias, {}


def create_field_info(
    field: DjangoField,
    serialization_alias: str,
    default: Any = PydanticUndefined,
    optional: bool = False,
    expanded: bool = False,
    default_factory: Optional[Callable[[], Any]] = None,
    **json_schema_extra: Any,
) -> FieldInfo:
    """
    Creates and returns a FieldInfo object for a given ORM field, configuring serialization and schema metadata.

    Args:
        field: The ORM field instance to extract information from.
        serialization_alias (str): The alias to use for serialization.
        default: The default value for the field. Defaults to PydanticUndefined.
        optional (bool): Whether the field is optional. If True, sets default to None. Defaults to False.
        expanded (bool): Whether the field should be marked as expanded in the schema. Defaults to False.
        default_factory (callable, optional): A callable that returns the default value for the field.
        **json_schema_extra: Additional keyword arguments to include in the JSON schema.

    Returns:
        FieldInfo: An object containing metadata for the field, suitable for use with Pydantic models.

    Notes:
        - If the field is marked as blank, null, or optional, the default is set to None.
        - The function extracts title and description from the field's verbose_name and help_text, if available.
        - Additional JSON schema metadata can be passed via keyword arguments.
    """

    orm_field_name, _, __, field_options = field.deconstruct()
    blank = field_options.get("blank", False)
    null = field_options.get("null", False)
    max_length = field_options.get("max_length")
    if blank or null or optional:
        default = None

    title = None
    description = getattr(field, "help_text", None)
    if getattr(field, "verbose_name", None):
        title = title_if_lower(field.verbose_name)
    return FieldInfo(
        default=default if default_factory is None else PydanticUndefined,
        default_factory=default_factory,
        alias=orm_field_name,
        validation_alias=AliasChoices(serialization_alias, orm_field_name),
        title=title,
        description=description,
        max_length=max_length,
        serialization_alias=serialization_alias,
        json_schema_extra={
            **json_schema_extra,
            "x-expanded": expanded,
        },
    )


FILTERS_MAP = {
    str: schema_filters.STRING_FILTERS,
    UUID: schema_filters.STRING_FILTERS,
    date: schema_filters.DATE_FILTERS,
    datetime: schema_filters.DATE_FILTERS,
    PeriodSchema: schema_filters.PERIOD_FILTERS,
    RangeSchema: schema_filters.RANGE_FILTERS,
    int: schema_filters.INTEGER_FILTERS,
    float: schema_filters.FLOAT_FILTERS,
    Measure: schema_filters.FLOAT_FILTERS,
    bool: schema_filters.BOOLEAN_FILTERS,
    CodedConceptSchema: schema_filters.CODED_CONCEPT_FILTERS,
    Username: schema_filters.USER_REFERENCE_FILTERS,
    Array[str]: schema_filters.ARRAY_FILTERS,  # type: ignore
    List[CodedConceptSchema]: schema_filters.MULTI_CODED_CONCEPT_FILTERS,
}


def get_schema_field_filters(
    field_name: str, field: FieldInfo
) -> List[SchemaFieldDefinition]:

    if field.annotation is None:
        warnings.warn(
            f"Field '{field_name}' has no annotation. Skipping filter generation.",
            UserWarning,
        )
        return []

    # Get schema field annotation
    annotation: Type[Any] = field.annotation

    # Check if field is optional
    if is_literal(annotation):
        return []

    filters = []
    # Check if field is optional
    if is_optional(annotation):
        filters += schema_filters.NULL_FILTERS
        _annotation = next(
            (arg for arg in get_args(annotation) if arg is not type(None)), None
        )
        if _annotation is None:
            warnings.warn(
                f"Field '{field_name}' annotation is only NoneType. Skipping filter generation.",
                UserWarning,
            )
            return []
        annotation = _annotation

    # Check if field is optional
    if is_union(annotation):
        if (
            len(get_args(annotation)) == 2
            and getattr(get_args(annotation)[1], "__origin__", None) == Array
            and get_args(get_args(annotation)[1]) == (str,)
        ):
            annotation = get_args(annotation)[1]
        else:
            annotation = get_args(annotation)[0]

    # Add the filters for the corresponding type
    filters += FILTERS_MAP.get(annotation, [])
    if field_name.endswith("Id") or field_name.endswith("Ids"):
        filters += schema_filters.REFERENCE_FILTERS
    if is_list(annotation):
        list_type = get_args(annotation)[0]
        if is_union(list_type):
            list_type = get_args(list_type)[0]
        if issubclass(list_type, PydanticBaseModel) and not issubclass(
            list_type, CodedConceptSchema
        ):
            subfield_filters = []
            for subfield_name, subfield in list_type.model_fields.items():
                if subfield_name in [
                    "description",
                    "createdBy",
                    "updatedBy",
                    "externalSourceId",
                ]:
                    continue
                subfield_filters.extend(
                    get_schema_field_filters(f"{field_name}.{subfield_name}", subfield)
                )
            return subfield_filters
        else:
            filters += FILTERS_MAP.get(list_type, [])

    if is_enum(annotation):
        for filter in schema_filters.ENUM_FILTERS:
            filter.value_type = (
                List[annotation] if is_list(filter.value_type) else annotation
            )
            filters.append(filter)
    if (
        not filters
        and isinstance(annotation, type)
        and issubclass(annotation, PydanticBaseModel)
        and not issubclass(annotation, CodedConceptSchema)
    ):
        subfield_filters = []
        for subfield_name, subfield in annotation.model_fields.items():
            if subfield_name in [
                "description",
                "createdBy",
                "updatedBy",
                "externalSourceId",
            ]:
                continue
            subfield_filters.extend(
                get_schema_field_filters(f"{field_name}.{subfield_name}", subfield)
            )
        return subfield_filters

    if not filters and annotation is not AnyObject:
        warnings.warn(
            f"Field '{field_name}' with annotation {annotation} could not be processed into any filters.",
            UserWarning,
        )
    # Construct the Pydantic fields for each filter
    definitions = []
    for filter in filters:
        filter_schema_attribute = (
            f"{field_name}.{filter.name}" if filter.name else field_name
        )
        # Provide a fallback for field.title if it is None
        field_title = field.title if field.title is not None else field_name
        definitions.append(
            SchemaFieldDefinition(
                name=filter_schema_attribute,
                python_type=filter.value_type,
                field_info=FieldInfo(
                    default=None,
                    description=f"{field_title} - {filter.description}",
                ),
                resolver_fcn=filter.generate_query_expression(
                    field=camel_to_snake(field_name)
                ),
            )
        )

    return definitions
