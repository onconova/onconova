

from dataclasses import dataclass 
from django.db.models import Q
from django.db.models.expressions import RawSQL

from enum import Enum
from typing import List, Tuple
from datetime import datetime, date
from functools import partial 

from pop.terminology.models import CodedConcept

class DjangoFilter:
    name: str = ''
    lookup: str = None
    description: str = ''  
    value_type: type
    negative: bool = False

    @staticmethod
    def query_expression(schema, value, field, lookup, negative):
        if value is None:
            return Q()
        query =  Q(**{f'{field}__{lookup}': value})
        return ~query if negative else query 
    
    @classmethod
    def generate_query_expression(cls, field: str):
        return partial(cls.query_expression, field=field, lookup=cls.lookup, negative=cls.negative)



class ExactStringFilter(DjangoFilter):
    name = ''
    description = 'Filter for full text matches'
    value_type = str
    lookup = 'iexact'
class NotExactStringFilter(ExactStringFilter):
    name = 'not'
    description = 'Filter for full text mismatches'
    value_type = str
    negative = True

class ContainsStringFilter(DjangoFilter):
    name = 'contains'
    description = 'Filter for partial text matches'
    value_type = str
    lookup = 'icontains'

class NotContainsStringFilter(ContainsStringFilter):
    name = 'not.contains'
    description = 'Filter for partial text mismatches'
    negative = True
    
class BeginsWithStringFilter(DjangoFilter):
    name = 'beginsWith'
    description = 'Filter for entries starting with the text'
    value_type = str
    lookup = 'istartswith'

class NotBeginsWithStringFilter(BeginsWithStringFilter):
    name='not.beginsWith'
    description='Filter for entries not starting with the text'
    negative = True

class EndsWithStringFilter(DjangoFilter):
    name='endsWith'
    description='Filter for entries ending with the text'
    value_type = str
    lookup='iendswith'

class NotEndsWithStringFilter(EndsWithStringFilter):
    name='not.endsWith'
    description='Filter for entries not ending with the text'
    negative = True

STRING_FILTERS = (
    ExactStringFilter, NotExactStringFilter,
    ContainsStringFilter, NotContainsStringFilter,
    BeginsWithStringFilter, NotBeginsWithStringFilter,
    EndsWithStringFilter, NotEndsWithStringFilter
)

    
class IsNullFilter(DjangoFilter):
    name='not.exists'
    description = 'Filter for entries without a value'
    value_type = bool
    lookup='isnull'

class NotIsNullFilter(IsNullFilter):
    name='exists'
    description = 'Filter for entries with a value'
    negative = True

NULL_FILTERS = (
    IsNullFilter, NotIsNullFilter
)

    
class BeforeDateFilter(DjangoFilter):
    name = 'before'
    lookup = 'lt'
    description = 'Filter for entries with dates before the specified value'
    value_type = date

class AfterDateFilter(DjangoFilter):
    name = 'after'
    lookup = 'gt'
    description = 'Filter for entries with dates after the specified value'
    value_type = date

class OnOrBeforeDateFilter(DjangoFilter):
    name = 'onOrBefore'
    lookup = 'lte'
    description = 'Filter for entries with dates on or before the specified value'
    value_type = date

class OnOrAfterDateFilter(DjangoFilter):
    name = 'onOrAfter'
    lookup = 'gte'
    description = 'Filter for entries with dates on or after the specified value'
    value_type = date

class OnDateFilter(DjangoFilter):
    name = 'on'
    lookup = 'exact'
    description = 'Filter for entries with dates exactly matching the specified value'
    value_type = date

class NotOnDateFilter(OnDateFilter):
    name = 'not.on'
    description = 'Filter for entries with dates not matching the specified value'
    negative = True

class BetweenDatesFilter(DjangoFilter):
    name = 'between'
    lookup = 'range'
    description = 'Filter for entries with dates between two specified values (inclusive)'
    value_type = Tuple[date, date]

class NotBetweenDatesFilter(BetweenDatesFilter):
    name = 'not.between'
    description = 'Filter for entries with dates not between two specified values (inclusive)'
    negative = True

DATE_FILTERS = (
    BeforeDateFilter, AfterDateFilter,
    OnOrBeforeDateFilter, OnOrAfterDateFilter,
    OnDateFilter, NotOnDateFilter,
    BetweenDatesFilter, NotBetweenDatesFilter
)

    

class LessThanIntegerFilter(DjangoFilter):
    name = 'lessThan'
    lookup = 'lt'
    description = 'Filter for entries with values less than the specified value'
    value_type = int

class LessThanOrEqualIntegerFilter(DjangoFilter):
    name = 'lessThanOrEqual'
    lookup = 'lte'
    description = 'Filter for entries with values less than or equal to the specified value'
    value_type = int

class GreaterThanIntegerFilter(DjangoFilter):
    name = 'greaterThan'
    lookup = 'gt'
    description = 'Filter for entries with values greater than the specified value'
    value_type = int

class GreaterThanOrEqualIntegerFilter(DjangoFilter):
    name = 'greaterThanOrEqual'
    lookup = 'gte'
    description = 'Filter for entries with values greater than or equal to the specified value'
    value_type = int

class EqualIntegerFilter(DjangoFilter):
    name = 'equal'
    lookup = 'exact'
    description = 'Filter for entries with values exactly equal to the specified value'
    value_type = int

class NotEqualIntegerFilter(EqualIntegerFilter):
    name = 'not.equal'
    description = 'Filter for entries with values not equal to the specified value'
    negative = True

class BetweenIntegerFilter(DjangoFilter):
    name = 'between'
    lookup = 'range'
    description = 'Filter for entries with values between two specified values (inclusive)'
    value_type = Tuple[int, int]

class NotBetweenIntegerFilter(BetweenIntegerFilter):
    name = 'not.between'
    description = 'Filter for entries with values between two specified values (inclusive)'
    negative = True


INTEGER_FILTERS = (
    LessThanIntegerFilter, LessThanOrEqualIntegerFilter,
    GreaterThanIntegerFilter, GreaterThanOrEqualIntegerFilter,
    EqualIntegerFilter, NotEqualIntegerFilter,
    BetweenIntegerFilter, NotBetweenIntegerFilter,
)


class LessThanFloatFilter(DjangoFilter):
    name = 'lessThan'
    lookup = 'lt'
    description = 'Filter for entries with values less than the specified value'
    value_type = float

class LessThanOrEqualFloatFilter(DjangoFilter):
    name = 'lessThanOrEqual'
    lookup = 'lte'
    description = 'Filter for entries with values less than or equal to the specified value'
    value_type = float

class GreaterThanFloatFilter(DjangoFilter):
    name = 'greaterThan'
    lookup = 'gt'
    description = 'Filter for entries with values greater than the specified value'
    value_type = float

class GreaterThanOrEqualFloatFilter(DjangoFilter):
    name = 'greaterThanOrEqual'
    lookup = 'gte'
    description = 'Filter for entries with values greater than or equal to the specified value'
    value_type = float

class EqualFloatFilter(DjangoFilter):
    name = 'equal'
    lookup = 'exact'
    description = 'Filter for entries with values exactly equal to the specified value'
    value_type = float

class NotEqualFloatFilter(EqualFloatFilter):
    name = 'not.equal'
    description = 'Filter for entries with values not equal to the specified value'
    negative = True

class BetweenFloatFilter(DjangoFilter):
    name = 'between'
    lookup = 'range'
    description = 'Filter for entries with values between two specified values (inclusive)'
    value_type = Tuple[float, float]

class NotBetweenFloatFilter(BetweenFloatFilter):
    name = 'not.between'
    description = 'Filter for entries with values between two specified values (inclusive)'
    negative = True

FLOAT_FILTERS = (
    LessThanFloatFilter, LessThanOrEqualFloatFilter,
    GreaterThanFloatFilter, GreaterThanOrEqualFloatFilter,
    EqualFloatFilter, NotEqualFloatFilter,
    BetweenFloatFilter, NotBetweenFloatFilter,
)


class EqualsBooleanFilter(DjangoFilter):
    name = ''
    lookup = 'exact'
    description = 'Filter for yes/no statement',
    value_type =  bool

BOOLEAN_FILTERS = (
    EqualsBooleanFilter,
)


class EqualsEnumFilter(DjangoFilter):
    name = ''
    lookup = 'exact'
    description = 'Filter for single value choice',
    value_type =  str

class NotEqualsEnumFilter(EqualsEnumFilter):
    name = 'not'
    description = 'Filter for all but a single value choice',
    negative = True

class AnyOfEnumFilter(DjangoFilter):
    name = 'anyOf'
    lookup = 'in'
    description = 'Filter for subset of value choices',
    value_type =  List[str]

class NotAnyOfEnumFilter(AnyOfEnumFilter):
    name = 'anyOf'
    description = 'Filter for excluding a subset of value choices',
    negative = True

ENUM_FILTERS = (
    EqualsEnumFilter, NotEqualsEnumFilter,
    AnyOfEnumFilter, NotAnyOfEnumFilter,
)
    
class EqualsReferenceFilter(DjangoFilter):
    name = ''
    lookup = 'exact'
    description = 'Filter for a matching reference Id'
    value_type = str

class NotEqualsReferenceFilter(EqualsReferenceFilter):
    name = 'not.equals'
    description = 'Filter for a mismatching reference Id'
    negative = True

class OneOfReferenceFilter(DjangoFilter):
    name = 'oneOf'
    lookup = 'in'
    description = 'Filter for a subset of matching reference Ids'
    value_type = List[str]

class NotOneOfReferenceFilter(OneOfReferenceFilter):
    name = 'not.oneOf'
    description = 'Filter for a subset of mismatching reference Ids'
    negative = True

REFERENCE_FILTERS = (
    EqualsReferenceFilter, NotEqualsReferenceFilter,
    OneOfReferenceFilter, NotOneOfReferenceFilter
)

    
class EqualsConceptFilter(DjangoFilter):
    name = ''
    lookup = 'code__iexact'
    description = 'Filter for a matching concept code'
    value_type = str

class NotEqualsConceptFilter(EqualsConceptFilter):
    name = 'not'
    description = 'Filter for a mismatching concept code'
    negative = True

class AnyOfConceptFilter(DjangoFilter):
    name = 'anyOf'
    lookup = 'code__in'
    description = 'Filter for a matching set of concept codes'
    value_type = List[str]

class NotAnyOfConceptFilter(AnyOfConceptFilter):
    name = 'not.anyOf'
    description = 'Filter for a mismmatching set of concept codes'
    negative = True

class DescendantsOfConceptFilter(DjangoFilter):
    name = 'descendantsOf'
    description = 'Filter for all child concepts of a given concepts code'
    value_type = str

    @staticmethod
    def query_expression(schema, value, field, lookup, negative):
        if value is None:
            return Q()
        terminology = schema._queryset_model._meta.get_field(field).related_model
        concept = terminology.objects.get(code=value)

        # Get the correct database table name
        db_table = terminology._meta.db_table  
        query =  Q(**{f'{field}__in': terminology.objects.filter(id__in=RawSQL(f"""
            WITH RECURSIVE descendants AS (
                SELECT id FROM {db_table} WHERE id = %s
                UNION ALL
                SELECT cc.id FROM {db_table} cc
                JOIN descendants d ON cc.parent_id = d.id
            )
            SELECT id FROM descendants WHERE id != %s
        """, [concept.id, concept.id]))})
        return ~query if negative else query

CODED_CONCEPT_FILTERS = (
    EqualsConceptFilter, NotEqualsConceptFilter,
    AnyOfConceptFilter, NotAnyOfConceptFilter,
    DescendantsOfConceptFilter, 
)



class OverlapsPeriodFilter(DjangoFilter):
    name = 'overlaps'
    lookup = 'overlap'
    description = 'Filter for entries overlapping with the time period'
    value_type = Tuple[date, date]

class NotOverlapsPeriodFilter(OverlapsPeriodFilter):
    name = 'not.overlaps'
    description = 'Filter for entries not overlapping with the time period'
    negative = True

class ContainsPeriodFilter(DjangoFilter):
    name = 'contains'
    lookup = 'contains'
    description = 'Filter for entries containing the time period'
    value_type = Tuple[date, date]

class NotContainsPeriodFilter(ContainsPeriodFilter):
    name = 'not.contains'
    description = 'Filter for entries not containing the time period'
    negative = True

class ContainedByPeriodFilter(DjangoFilter):
    name = 'containedBy'
    lookup = 'contained_by'
    description = 'Filter for entries whose period are contined by the time period'
    value_type = Tuple[date, date]

class NotContainedByPeriodFilter(ContainedByPeriodFilter):
    name = 'not.containedBy'
    description = 'Filter for entries whose period are not contined by the time period'
    negative = True
    

PERIOD_FILTERS = (
    OverlapsPeriodFilter, NotOverlapsPeriodFilter,
    ContainsPeriodFilter, NotContainsPeriodFilter,
    ContainedByPeriodFilter, NotContainedByPeriodFilter,
)

    

class ExactRefereceFilter(DjangoFilter):
    name = ''
    description = 'Filter for reference matches'
    value_type = str
    lookup = 'exact'
class NotExactRefereceFilter(ExactStringFilter):
    name = 'not'
    description = 'Filter for reference mismatches'
    value_type = str
    negative = True

REFERENCE_FILTERS = (
    ExactRefereceFilter, NotExactRefereceFilter,
)