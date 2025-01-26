from typing import get_args, List, Tuple, Optional
import enum 
import warnings
from datetime import date, datetime

from django.contrib.postgres.fields import DateRangeField, BigIntegerRangeField
from django.db.models.fields import Field as DjangoField
from django.db.models import CharField
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

from ninja.orm.fields import TYPES as BASE_TYPES, title_if_lower

from pydantic import AliasChoices, BaseModel as PydanticBaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from pop.terminology.models import CodedConcept as CodedConceptModel
from pop.core.schemas import CodedConceptSchema, PeriodSchema, RangeSchema
from pop.core.measures import MeasureSchema
from pop.core.schemas import filters as schema_filters
from pop.core.utils import is_list, is_optional, is_literal, is_enum, to_camel_case
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
    json_schema_extra = dict(
        orm_name = django_field_name,    
        is_relation = bool(field.is_relation),
        many_to_many = bool(field.many_to_many),
        one_to_many = bool(field.one_to_many),
        expanded = expand,
    )
    
    is_array_field = isinstance(field, ArrayField)
    if is_array_field:
        field = field.base_field

    # Handle relation fields
    if field.is_relation:
        if expand:
            from pop.core.schemas import create_schema
            model = field.related_model
            if field.one_to_many:
                if not exclude_related_fields:
                    exclude_related_fields = []
                exclude_related_fields.append(field.field.name)
            schema = create_schema(model, exclude=exclude_related_fields, name=expand)
            if not field.concrete and field.auto_created or field.null:
                default = None
            if field.one_to_many or field.many_to_many:
                schema = List[schema]
                default=[]

            python_type = schema
        else:
            related_model = field.related_model 
            if issubclass(related_model, CodedConceptModel):
                json_schema_extra['terminology'] = related_model.__name__
                related_type = CodedConceptSchema   
            else:
                internal_type = related_model._meta.get_field('id').get_internal_type()
                django_field_name += '_id'

            if not field.concrete and field.auto_created or field.null or field.blank or optional:
                default = None
                nullable = True

            if not related_type:
                related_type = DJANGO_TO_PYDANTIC_TYPES.get(internal_type, int)

            if field.one_to_many or field.many_to_many:
                python_type = List[related_type] 
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
            python_type = MeasureSchema
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

        if field.primary_key or blank or null or optional:
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

    if nullable:
        python_type = Optional[python_type] 

    description = getattr(field,'help_text', None)
    if  getattr(field,'verbose_name', None):
        title = title_if_lower(field.verbose_name)


    schema_field_name = to_camel_case(django_field_name)
    return schema_field_name, (
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
            json_schema_extra=json_schema_extra,
        ),
    )

    
FILTERS_MAP = {
    str: schema_filters.StringFilters.values(),
    type(enum.Enum): schema_filters.StringFilters.values(),
    date: schema_filters.DateFilters.values(),
    datetime: schema_filters.DateFilters.values(),
    int: schema_filters.IntegerFilters.values(),
    float: schema_filters.FloatFilters.values(),
    MeasureSchema: schema_filters.FloatFilters.values(),
    bool: schema_filters.BooleanFilters.values(),
    CodedConceptSchema: schema_filters.CodedConceptFilters.values(),
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
        filters += schema_filters.NullFilters.values() 
        annotation = get_args(annotation)[0]

        
    # Add the filters for the corresponding type        
    filters += FILTERS_MAP.get(annotation, [])
    if field_name.endswith('Id') or field_name.endswith('Ids'):
        filters += schema_filters.ReferenceFilters.values() 
    if is_list(annotation):
        list_type = get_args(annotation)[0]
        if issubclass(list_type, PydanticBaseModel):
            subfield_filters = []
            for subfield_name, subfield in list_type.model_fields.items():
                subfield_filters.extend(get_schema_field_filters(f'{field_name}.{subfield_name}', subfield))
            return subfield_filters 
                 
    if is_enum(annotation):
        filters.append(schema_filters.FilterDetails(
            name='',
            value_type = annotation, 
            django_lookup = '',
            description = 'Filter for one of the value choices',
        ))
        filters.append(schema_filters.FilterDetails(
            name='allOf',
            value_type = List[annotation], 
            django_lookup = 'in',
            description = 'Filter for some of the value choices',
        ))
    if not filters:
        warnings.warn(f"No filters defined for field type: {annotation}")
    
    # Construct the Pydantic fields for each filter
    return [ 
        (
            f'{field_name}.{filter.name}' if filter.name else field_name, 
            ( filter.value_type, FieldInfo(
                default=None,
                description=f'{field.title} - {filter.description}',
                json_schema_extra={
                    'negative': filter.negative,
                    'django_lookup': f'{field.alias}__{filter.django_lookup}',
                }
            ))
        )
        for filter in filters
    ]

