from typing import get_args, List, Tuple, Optional
import enum 
import warnings
from uuid import UUID
from datetime import date, datetime
from functools import partial 
from django.contrib.postgres.fields import DateRangeField, BigIntegerRangeField
from django.db.models.fields import Field as DjangoField
from django.db.models import CharField
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

from ninja.orm.fields import TYPES as BASE_TYPES, title_if_lower

from pydantic import AliasChoices, BaseModel as PydanticBaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined #type: ignore

from pop.terminology.models import CodedConcept as CodedConceptModel
from pop.core.schemas import CodedConceptSchema, PeriodSchema, RangeSchema
from pop.core.measures import Measure
from pop.core import filters as schema_filters
from pop.core.utils import is_list, is_optional, is_literal, is_enum, to_camel_case, camel_to_snake
from pop.core.measures.fields import MeasurementField

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
    """
    Returns a pydantic field from a django model field.

    This function takes a django model field and returns a tuple containing the
    python type for the field and a pydantic FieldInfo object. The python type
    is determined by the field's internal type and whether or not the field is
    a relation field. The FieldInfo object contains additional information about
    the field such as its default value, alias, title, description, and json
    schema extras.

    Args:
        field (DjangoField): The django model field to convert.
        expand (bool, optional): Whether to expand the relation field. Defaults to False.
        optional (bool, optional): Whether the field is optional. Defaults to False.

    Returns:
        Tuple[type, FieldInfo]: A tuple containing the python type for the field and a pydantic FieldInfo object.
    """
    django_field_name = getattr(field, "name", None) and field.name
    default = ...
    default_factory = None
    description = None
    title = None
    max_length = None
    nullable = False
    python_type = None
    related_type = None
    examples = []    
    json_schema_extra = {}
    expanded = expand
    resolver_fcn = None
    is_array_field = isinstance(field, ArrayField)
    if is_array_field:
        field = field.base_field

    # Handle relation fields
    if field.is_relation:
        if expand:
            from .base import BaseSchema
            from .factory import create_schema
            model = field.related_model
            if field.one_to_many:
                if not exclude_related_fields:
                    exclude_related_fields = []
                exclude_related_fields.append(field.field.name)
            schema = create_schema(model, exclude=exclude_related_fields, name=expand)
            if not field.concrete and field.auto_created or field.null:
                default = None
            if field.one_to_many or field.many_to_many:
                resolver_fcn = partial(BaseSchema._resolve_expanded_many_to_many, orm_field_name=field.name, related_schema=schema)
                schema = List[schema]
                default=[]
            else:
                resolver_fcn = partial(BaseSchema._resolve_expanded_foreign_key, orm_field_name=field.name, related_schema=schema)
            python_type = schema
        else:
            related_model = field.related_model 
            if issubclass(related_model, CodedConceptModel):
                json_schema_extra['x-terminology'] = related_model.__name__
                related_type = CodedConceptSchema   
            elif issubclass(related_model, UserModel):
                expanded = True
                from pop.core.schemas.user import UserSchema
                related_type = UserSchema   
            else:
                from .base import BaseSchema
                resolver_fcn = partial(BaseSchema._resolve_foreign_key, orm_field_name=field.name)
                internal_type = related_model._meta.get_field('id').get_internal_type()
                django_field_name += '_id'

            if not field.concrete and field.auto_created or field.null or field.blank or optional:
                default = None
                nullable = True

            if not related_type:
                related_type = DJANGO_TO_PYDANTIC_TYPES.get(internal_type, int)

            if field.one_to_many or field.many_to_many:
                python_type = List[related_type] 
                if django_field_name not in ['created_by', 'updated_by']:
                    from .base import BaseSchema
                    resolver_fcn = partial(BaseSchema._resolve_many_to_many, orm_field_name=field.name)
                    if not django_field_name.endswith('s'):
                        django_field_name += 's'
                default=[]
            else:
                python_type = related_type
    
    else:
        
        # Handle non-relation fields
        _f_name, _f_path, _f_pos, field_options = field.deconstruct()
        blank = field_options.get("blank", False)
        null = field_options.get("null", False)
        max_length = field_options.get("max_length")

        if isinstance(field, MeasurementField):
            python_type = Measure
        elif isinstance(field, DateRangeField):
            python_type = PeriodSchema
        elif isinstance(field, BigIntegerRangeField):
            python_type = RangeSchema
        elif isinstance(field, CharField) and field.choices is not None:            
            schema_field_name = to_camel_case(django_field_name)
            enum_schema_name = f'{field.model.__name__ if hasattr(field, "model") else ""}{schema_field_name[0].upper()+schema_field_name[1:]}Choices'
            enum_choices = enum.Enum(enum_schema_name, {value.upper(): value for value,_ in field.choices}, type=str)
            python_type = enum_choices
        else:
            internal_type = field.get_internal_type()
            python_type = DJANGO_TO_PYDANTIC_TYPES[internal_type]

        if blank or null or optional:
            default = None
            nullable = True

        if field.has_default():
            if callable(field.default):
                default_factory = field.default
            else:
                default = field.default

    if is_array_field:
        if not django_field_name.endswith('s'):
            django_field_name += 's'
        python_type = List[python_type]

    if default_factory:
        default = PydanticUndefined

    if field.primary_key:
        default = PydanticUndefined
        default_factory = PydanticUndefined
    
    if nullable:
        python_type = Optional[python_type] 

    description = getattr(field,'help_text', None)
    if  getattr(field,'verbose_name', None):
        title = title_if_lower(field.verbose_name)


    schema_field_name = to_camel_case(django_field_name)
    return resolver_fcn, schema_field_name, (
        python_type,
        FieldInfo(
            default=default,
            default_factory=default_factory,
            alias=django_field_name,
            validation_alias=AliasChoices(schema_field_name, django_field_name),
            serialization_alias=schema_field_name,
            title=title,
            examples=examples,
            description=description,
            max_length=max_length,
            json_schema_extra={
                **json_schema_extra,
                'x-expanded': expanded,
            },
        ),
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

    # Add the filters for the corresponding type        
    filters += FILTERS_MAP.get(annotation, [])
    if field_name.endswith('Id') or field_name.endswith('Ids'):
        filters += schema_filters.REFERENCE_FILTERS
    if is_list(annotation):
        list_type = get_args(annotation)[0]
        if issubclass(list_type, PydanticBaseModel):
            subfield_filters = []
            for subfield_name, subfield in list_type.model_fields.items():
                if subfield_name in ['description', 'createdAt', 'createdBy', 'updatedBy', 'updatedAt', 'externalSourceId', 'externalSource']:
                    continue
                subfield_filters.extend(get_schema_field_filters(f'{field_name}.{subfield_name}', subfield))
            return subfield_filters 
                 
    if is_enum(annotation):
        for filter in schema_filters.ENUM_FILTERS:
            filter.value_type = List[annotation] if is_list(filter.value_type) else annotation
            filters.append(filter)

    if not filters:
        warnings.warn(f"No filters defined for field type: {annotation}")
    
    # Construct the Pydantic fields for each filter
    filter_infos = []
    for filter in filters:
        filter_schema_attribute = f'{field_name}.{filter.name}' if filter.name else field_name
        filter_infos.append((
            filter_schema_attribute,
            ( filter.value_type, FieldInfo(
                default=None,
                description=f'{field.title} - {filter.description}',
            )),
            (f"filter_{filter_schema_attribute.replace('.','_')}", filter.generate_query_expression(field=camel_to_snake(field_name)))
        ))
    return filter_infos

