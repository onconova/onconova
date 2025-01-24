from typing import Literal, List, Tuple, Optional
import enum 
import warnings
from datetime import date, datetime

from django.contrib.postgres.fields import DateRangeField, BigIntegerRangeField
from django.db.models.fields import Field as DjangoField
from django.db.models import CharField
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField


from ninja.orm.fields import TYPES as BASE_TYPES, title_if_lower, create_m2m_link_type
from ninja.schema import Schema 

from pydantic import AliasChoices
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from pop.terminology.models import CodedConcept as CodedConceptModel
from pop.core.schemas import CodedConceptSchema, MeasureSchema, PeriodSchema, RangeSchema
from pop.core.fields import MeasurementField

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


from dataclasses import dataclass 
from enum import Enum


class FilterEnum(Enum):
    
    @classmethod
    def values(cls):
        return [c.value for c in cls]

@dataclass
class LookupDetails:
    django_lookup: str
    value_type: str
    name: str 
    description: str = ''
    negative: bool = False 

    def invert_logic(self, name, description):
        return LookupDetails(
            name = name,
            description=description,
            value_type=self.value_type,
            django_lookup = self.django_lookup,
            negative = not self.negative
        )

class StringFilters(FilterEnum):
    matches = LookupDetails(
        name='',
        value_type = str, 
        django_lookup = 'exact',
        description = 'Filter for full text matches',
    )
    notMatches = matches.invert_logic(
        name='not',
        description = 'Filter for full text mismatches'
    )
    contains = LookupDetails(
        name='contains',
        value_type = str, 
        django_lookup = 'contains',
        description = 'Filter for partial text matches'
    )
    notContains = contains.invert_logic(
        name='not.contains',
        description = 'Filter for partial text mismatches'
    )
    beginsWith = LookupDetails(
        name='beginsWith',
        value_type = str, 
        django_lookup = 'begins_with',
        description = 'Filter for entries starting with the text'
    )
    notBeginsWith = beginsWith.invert_logic(
        name='not.beginsWith',
        description = 'Filter for entries not starting with the text'
    )
    endsWith = LookupDetails(
        name='endsWith',
        value_type = str, 
        django_lookup = 'ends_with',
        description = 'Filter for entries ending with the text'
    )
    notEndsWith = endsWith.invert_logic(
        name = 'not.endsWith',
        description = 'Filter for entries not ending with the text'
    )
    

class NullFilters(FilterEnum):
    exists = LookupDetails(
        name = 'exists',
        value_type = str, 
        django_lookup = 'is_null',
        negative = True,
        description = 'Filter for entries without a value'
    )
    notExists = exists.invert_logic(
        name='not.exists',
        description = 'Filter for entries with a value'
    )
    
class DateFilters(FilterEnum):
    before = LookupDetails(
        name='before',
        value_type=date,
        django_lookup='lt',
        description='Filter for entries with dates before the specified value'
    )
    after = LookupDetails(
        name='after',
        value_type=date,
        django_lookup='gt',
        description='Filter for entries with dates after the specified value'
    )
    onOrBefore = LookupDetails(
        name='onOrBefore',
        value_type=date,
        django_lookup='lte',
        description='Filter for entries with dates on or before the specified value'
    )
    onOrAfter = LookupDetails(
        name='onOrAfter',
        value_type=date,
        django_lookup='gte',
        description='Filter for entries with dates on or after the specified value'
    )
    on = LookupDetails(
        name='on',
        value_type=date,
        django_lookup='exact',
        description='Filter for entries with dates exactly matching the specified value'
    )
    notOn = on.invert_logic(
        name='not.on',
        description='Filter for entries with dates not matching the specified value'
    )
    between = LookupDetails(
        name='between',
        value_type=Tuple[date,date],  # A tuple of two ISO 8601 date strings
        django_lookup='range',
        description='Filter for entries with dates between two specified values (inclusive)'
    )
    noBetween = between.invert_logic(
        name='not.between',
        description='Filter for entries with dates not between two specified values (inclusive)'
    )
    
    
class IntegerFilters(FilterEnum):
    lessThan = LookupDetails(
        name='lessThan',
        value_type=int, 
        django_lookup='lt',
        description='Filter for entries with values less than the specified value'
    )
    lessThanOrEqual = LookupDetails(
        name='lessThanOrEqual',
        value_type=int, 
        django_lookup='lte',
        description='Filter for entries with values less than or equal to the specified value'
    )
    greaterThan = LookupDetails(
        name='greaterThan',
        value_type=int, 
        django_lookup='gt',
        description='Filter for entries with values greater than the specified value'
    )
    greaterThanOrEqual = LookupDetails(
        name='greaterThanOrEqual',
        value_type=int,  
        django_lookup='gte',
        description='Filter for entries with values greater than or equal to the specified value'
    )
    equal = LookupDetails(
        name='equal',
        value_type=int, 
        django_lookup='exact',
        description='Filter for entries with values exactly equal to the specified value'
    )
    notEqual = equal.invert_logic(
        name='not.equal',
        description='Filter for entries with values not equal to the specified value'
    )
    between = LookupDetails(
        name='between',
        value_type=Tuple[int, int], 
        django_lookup='range',
        description='Filter for entries with values between two specified values (inclusive)'
    )
    valueExists = LookupDetails(
        name='exists',
        value_type=int, 
        django_lookup='isnull',
        negative=True,
        description='Filter for entries where the value exists'
    )
    valueNotExists = valueExists.invert_logic(
        name='not.exists',
        description='Filter for entries where the value does not exist'
    )

class FloatFilters(FilterEnum):
    lessThan = LookupDetails(
        name='lessThan',
        value_type=float, 
        django_lookup='lt',
        description='Filter for entries with values less than the specified value'
    )
    lessThanOrEqual = LookupDetails(
        name='lessThanOrEqual',
        value_type=float, 
        django_lookup='lte',
        description='Filter for entries with values less than or equal to the specified value'
    )
    greaterThan = LookupDetails(
        name='greaterThan',
        value_type=float, 
        django_lookup='gt',
        description='Filter for entries with values greater than the specified value'
    )
    greaterThanOrEqual = LookupDetails(
        name='greaterThanOrEqual',
        value_type=float,  
        django_lookup='gte',
        description='Filter for entries with values greater than or equal to the specified value'
    )
    equal = LookupDetails(
        name='equal',
        value_type=float, 
        django_lookup='exact',
        description='Filter for entries with values exactly equal to the specified value'
    )
    notEqual = equal.invert_logic(
        name='not.equal',
        description='Filter for entries with values not equal to the specified value'
    )
    between = LookupDetails(
        name='between',
        value_type=Tuple[float, float], 
        django_lookup='range',
        description='Filter for entries with values between two specified values (inclusive)'
    )
    valueExists = LookupDetails(
        name='exists',
        value_type=float, 
        django_lookup='isnull',
        negative=True,
        description='Filter for entries where the value exists'
    )
    valueNotExists = valueExists.invert_logic(
        name='not.exists',
        description='Filter for entries where the value does not exist'
    )
    
class BooleanFilters(FilterEnum):
    equals = LookupDetails(
        name='',
        value_type = bool, 
        django_lookup = 'equals',
        description = 'Filter for yes/no statement',
    )
    
    
class ReferenceFilters(FilterEnum):
    equals = LookupDetails(
        name='',
        value_type = str, 
        django_lookup = 'equals',
        description = 'Filter for a matching reference Id',
    )
    notEquals = equals.invert_logic(
        name='not.equals',
        description = 'Filter for a mismatching reference Id',
    )
    oneOf = LookupDetails(
        name='oneOf',
        value_type = List[str], 
        django_lookup = 'in',
        description = 'Filter for a subset of matching reference Ids',
    )
    notOneOf = oneOf.invert_logic(
        name='not.oneOf',
        description = 'Filter for a subset of mismatching reference Ids',
    )
    
class CodedConceptFilters(FilterEnum):
    codeEquals = LookupDetails(
        name='code',
        value_type = str, 
        django_lookup = 'code',
        description = 'Filter for a matching code',
    )
    codeIncludes = LookupDetails(
        name='code.includes',
        value_type = List[str], 
        django_lookup = 'code__in',
        description = 'Filter for a matching set of codes',
    )
    codeContains = LookupDetails(
        name='code.contains',
        value_type = List[str], 
        django_lookup = 'code__in',
        description = 'Filter for partially matching codes',
    )
    displayEquals = LookupDetails(
        name='display',
        value_type = str, 
        django_lookup = 'display',
        description = 'Filter for a fully matching concept text',
    )
    displayContains = LookupDetails(
        name='display.contains',
        value_type = str, 
        django_lookup = 'display__icontains',
        description = 'Filter for a partially matching concept text',
    )
    codeDescendsFrom = LookupDetails(
        name='code.descendsFrom',
        value_type = List[str], 
        django_lookup = 'descendsfrom__code',
        description = 'Filter for all child concept of a given code',
    )
    
FILTERS_MAP = {
    str: StringFilters.values(),
    type(Enum): StringFilters.values(),
    date: DateFilters.values(),
    datetime: DateFilters.values(),
    int: IntegerFilters.values(),
    float: FloatFilters.values(),
    MeasureSchema: FloatFilters.values(),
    bool: BooleanFilters.values(),
    CodedConceptSchema: CodedConceptFilters.values(),
}

from typing import Union, get_args, get_origin
from ninja import Schema 
def get_schema_field_filters(field_name: str, field: FieldInfo):
    
    # Get schema field annotation 
    annotation = field.annotation

    # Check if field is optional
    if is_literal(annotation):
        return []

    filters = [] 
    # Check if field is optional
    if is_optional(annotation):
        filters += NullFilters.values() 
        annotation = get_args(annotation)[0]

        
    # Add the filters for the corresponding type        
    filters += FILTERS_MAP.get(annotation, [])
    if field_name.endswith('Id') or field_name.endswith('Ids'):
        filters += ReferenceFilters.values() 
    if is_list(annotation):
        list_type = get_args(annotation)[0]
        # if issubclass(list_type, Schema):
        #     return get_schema_field_filters(list_type)
    if is_enum(annotation):
        filters.append(LookupDetails(
            name='',
            value_type = annotation, 
            django_lookup = '',
            description = 'Filter for one of the value choices',
        ))
        filters.append(LookupDetails(
            name='allOf',
            value_type = List[annotation], 
            django_lookup = 'in',
            description = 'Filter for some of the value choices',
        ))
    if not filters:
        warnings.warn(f"No filters defined for field type: {annotation} of {annotation.__class__}")
    
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


def is_optional(field):
    return get_origin(field) is Union and \
           type(None) in get_args(field)

def is_list(field):
    return get_origin(field) is List 

def is_enum(field):
    return field.__class__ is type(Enum)

def is_literal(field):
    return get_origin(field) is Literal 

def to_camel_case(string: str) -> str:
    """
    Convert a string from snake_case to camelCase.

    Args:
        string (str): The string to convert.

    Returns:
        str: The converted string.
    """
    return ''.join([
        word if n==0 else word.capitalize()
            for n,word in enumerate(string.split('_'))
    ])

