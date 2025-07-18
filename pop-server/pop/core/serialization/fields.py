import enum
import warnings
from datetime import date, datetime
from functools import partial
from typing import List, Tuple, Union, get_args
from uuid import UUID

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import (
    ArrayField,
    BigIntegerRangeField,
    DateRangeField,
    IntegerRangeField,
)
from django.db.models import CharField
from django.db.models.fields import Field as DjangoField
from ninja.orm.fields import TYPES as BASE_TYPES
from ninja.orm.fields import title_if_lower
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
from pydantic import UUID4, AliasChoices
from pydantic import BaseModel as PydanticBaseModel
from pydantic import constr
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined  # type: ignore
from typing_extensions import TypeAliasType

UserModel = get_user_model()

DJANGO_TO_PYDANTIC_TYPES = {
    **BASE_TYPES,
}


def get_schema_field(
    field: DjangoField,
    *,
    expand: bool = False,
    optional: bool = False,
    exclude_related_fields: List[str] = [],
) -> Tuple[type, FieldInfo]:
    default = ...
    default_factory = None
    resolver_fcn = None
    is_array_field = isinstance(field, ArrayField)
    extras = {}
    if is_array_field:
        field = field.base_field
    if field.is_relation:
        resolver_fcn, python_type, serialization_alias, default, extras = (
            process_relation_field(field, exclude_related_fields, expand)
        )

    else:
        (
            resolver_fcn,
            python_type,
            serialization_alias,
            default,
            default_factory,
            extras,
        ) = process_non_relation_field(field)
        if is_array_field:
            python_type = List[python_type]
    extras.update({"x-expanded": expand})
    field_info = create_field_info(
        field,
        serialization_alias,
        default=default,
        default_factory=default_factory,
        optional=optional,
        **extras,
    )
    if field_info.default is None:
        python_type = Nullable[python_type]
    return resolver_fcn, serialization_alias, (python_type, field_info)


def process_non_relation_field(field):
    from .base import BaseSchema

    extras = {}
    resolver_fcn = None
    serialization_alias = to_camel_case(field.name)
    internal_type = field.get_internal_type()
    if isinstance(field, MeasurementField):
        python_type = Measure
        resolver_fcn = partial(BaseSchema._resolve_measure, orm_field_name=field.name)
        extras["x-measure"] = field.measurement.__name__
        extras["x-default-unit"] = field.get_default_unit().replace("__", "/")

    elif isinstance(field, DateRangeField):
        python_type = PeriodSchema
    elif isinstance(field, (BigIntegerRangeField, IntegerRangeField)):
        python_type = RangeSchema
    elif isinstance(field, CharField) and field.choices is not None:
        python_type = enum.Enum(
            f"{field.model.__name__ if hasattr(field, 'model') else ''}{to_camel_case(field.name)[0].upper() + to_camel_case(field.name)[1:]}Choices",
            {value.upper(): value for value, _ in field.choices},
            type=str,
        )
    else:
        python_type = DJANGO_TO_PYDANTIC_TYPES.get(internal_type, str)

    if field.has_default() and not field.primary_key:
        default = field.default() if callable(field.default) else field.default
        default_factory = field.default if callable(field.default) else None
    else:
        default, default_factory = PydanticUndefined, None

    return (
        resolver_fcn,
        python_type,
        serialization_alias,
        default,
        default_factory,
        extras,
    )


def process_relation_field(field, exclude_related_fields=None, expand=False):
    from .base import BaseSchema
    from .factory import create_schema

    is_many_related = field.one_to_many or field.many_to_many
    serialization_alias = to_camel_case(field.name)
    related_model = field.related_model
    extras = {}
    if expand:
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
        resolver_fcn, related_type, serialization_alias, extras = (
            get_related_field_type(field, related_model, serialization_alias)
        )
        python_type = List[related_type] if is_many_related else related_type

    optional = field.concrete and field.auto_created or field.null or field.blank
    default = [] if is_many_related else (None if optional else PydanticUndefined)

    return resolver_fcn, python_type, serialization_alias, default, extras


def get_related_field_type(field, related_model, serialization_alias):
    from .base import BaseSchema

    if issubclass(related_model, CodedConceptModel):
        extras = {"x-terminology": related_model.__name__}
        return None, CodedConceptSchema, serialization_alias, extras
    if issubclass(related_model, UserModel):
        return (
            partial(
                BaseSchema._resolve_user,
                orm_field_name=field.name,
                many=field.many_to_many,
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
    field,
    serialization_alias,
    default=PydanticUndefined,
    optional=False,
    expanded=False,
    default_factory=None,
    **json_schema_extra,
):

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
    int: schema_filters.INTEGER_FILTERS,
    float: schema_filters.FLOAT_FILTERS,
    Measure: schema_filters.FLOAT_FILTERS,
    bool: schema_filters.BOOLEAN_FILTERS,
    CodedConceptSchema: schema_filters.CODED_CONCEPT_FILTERS,
    Username: schema_filters.USER_REFERENCE_FILTERS,
    Array[str]: schema_filters.ARRAY_FILTERS,
    List[CodedConceptSchema]: schema_filters.MULTI_CODED_CONCEPT_FILTERS,
}


def get_schema_field_filters(field_name: str, field: FieldInfo):

    # Get schema field annotation
    annotation = field.annotation

    # Check if field is optional
    if is_literal(annotation):
        return []

    filters = []
    # Check if field is optional
    if is_optional(annotation):
        filters += schema_filters.NULL_FILTERS
        annotation = get_args(annotation)[0]

    # Check if field is optional
    if is_union(annotation):
        if len(get_args(annotation)) == 2 and get_args(annotation)[1] == Array[str]:
            annotation = Array[str]
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
                    "createdAt",
                    "createdBy",
                    "updatedBy",
                    "updatedAt",
                    "externalSourceId",
                    "externalSource",
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
        and issubclass(annotation, PydanticBaseModel)
        and not issubclass(annotation, CodedConceptSchema)
    ):
        subfield_filters = []
        for subfield_name, subfield in annotation.model_fields.items():
            if subfield_name in [
                "description",
                "createdAt",
                "createdBy",
                "updatedBy",
                "updatedAt",
                "externalSourceId",
                "externalSource",
            ]:
                continue
            subfield_filters.extend(
                get_schema_field_filters(f"{field_name}.{subfield_name}", subfield)
            )
        return subfield_filters

    if not filters:
        warnings.warn(f"No filters defined for field type: {annotation}")

    # Construct the Pydantic fields for each filter
    filter_infos = []
    for filter in filters:
        filter_schema_attribute = (
            f"{field_name}.{filter.name}" if filter.name else field_name
        )
        filter_infos.append(
            (
                filter_schema_attribute,
                (
                    filter.value_type,
                    FieldInfo(
                        default=None,
                        description=f"{field.title} - {filter.description}",
                    ),
                ),
                (
                    f"filter_{filter_schema_attribute.replace('.','_')}",
                    filter.generate_query_expression(field=camel_to_snake(field_name)),
                ),
            )
        )
    return filter_infos
