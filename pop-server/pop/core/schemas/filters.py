

from dataclasses import dataclass 
from enum import Enum
from typing import List, Tuple
from datetime import datetime, date

class FilterEnum(Enum):
    """
    A base class for all enumerations that are used as Filters.

    The values method returns a list of all the values in the enumeration.
    """
    @classmethod
    def values(cls):
        """
        Returns a list of all the values in the enumeration.
        """
        return [c.value for c in cls]

@dataclass
class FilterDetails:
    """
    A dataclass to represent the details of a filter.

    Args:
        django_lookup (str): The Django ORM lookup string.
        value_type (str): The type of the value that the filter expects.
        name (str): A name for the filter.
        description (str): A description of the filter.
        negative (bool): A flag indicating whether the filter should be applied
            with inverted logic.
    """
    django_lookup: str
    value_type: str
    name: str 
    description: str = ''
    negative: bool = False 

    def invert_logic(self, name, description):
        """
        Creates a new FilterDetails instance with inverted logic.

        Args:
            name (str): The name for the new lookup.
            description (str): The description for the new lookup.

        Returns:
            FilterDetails: A new instance with the logic inverted, retaining
            the same value_type and django_lookup, but with the negative flag
            flipped.
        """
        return FilterDetails(
            name = name,
            description=description,
            value_type=self.value_type,
            django_lookup = self.django_lookup,
            negative = not self.negative
        )

class StringFilters(FilterEnum):
    """
    An enumerationclass containing filter details for string field values.
    """
    matches = FilterDetails(
        name='',
        value_type = str, 
        django_lookup = 'exact',
        description = 'Filter for full text matches',
    )
    notMatches = matches.invert_logic(
        name='not',
        description = 'Filter for full text mismatches'
    )
    contains = FilterDetails(
        name='contains',
        value_type = str, 
        django_lookup = 'contains',
        description = 'Filter for partial text matches'
    )
    notContains = contains.invert_logic(
        name='not.contains',
        description = 'Filter for partial text mismatches'
    )
    beginsWith = FilterDetails(
        name='beginsWith',
        value_type = str, 
        django_lookup = 'begins_with',
        description = 'Filter for entries starting with the text'
    )
    notBeginsWith = beginsWith.invert_logic(
        name='not.beginsWith',
        description = 'Filter for entries not starting with the text'
    )
    endsWith = FilterDetails(
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
    """
    An enumerationclass containing filter details for null field values.
    """
    exists = FilterDetails(
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
    """
    An enumerationclass containing filter details for date field values.
    """
    before = FilterDetails(
        name='before',
        value_type=date,
        django_lookup='lt',
        description='Filter for entries with dates before the specified value'
    )
    after = FilterDetails(
        name='after',
        value_type=date,
        django_lookup='gt',
        description='Filter for entries with dates after the specified value'
    )
    onOrBefore = FilterDetails(
        name='onOrBefore',
        value_type=date,
        django_lookup='lte',
        description='Filter for entries with dates on or before the specified value'
    )
    onOrAfter = FilterDetails(
        name='onOrAfter',
        value_type=date,
        django_lookup='gte',
        description='Filter for entries with dates on or after the specified value'
    )
    on = FilterDetails(
        name='on',
        value_type=date,
        django_lookup='exact',
        description='Filter for entries with dates exactly matching the specified value'
    )
    notOn = on.invert_logic(
        name='not.on',
        description='Filter for entries with dates not matching the specified value'
    )
    between = FilterDetails(
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
    """
    An enumerationclass containing filter details for integer field values.
    """
    lessThan = FilterDetails(
        name='lessThan',
        value_type=int, 
        django_lookup='lt',
        description='Filter for entries with values less than the specified value'
    )
    lessThanOrEqual = FilterDetails(
        name='lessThanOrEqual',
        value_type=int, 
        django_lookup='lte',
        description='Filter for entries with values less than or equal to the specified value'
    )
    greaterThan = FilterDetails(
        name='greaterThan',
        value_type=int, 
        django_lookup='gt',
        description='Filter for entries with values greater than the specified value'
    )
    greaterThanOrEqual = FilterDetails(
        name='greaterThanOrEqual',
        value_type=int,  
        django_lookup='gte',
        description='Filter for entries with values greater than or equal to the specified value'
    )
    equal = FilterDetails(
        name='equal',
        value_type=int, 
        django_lookup='exact',
        description='Filter for entries with values exactly equal to the specified value'
    )
    notEqual = equal.invert_logic(
        name='not.equal',
        description='Filter for entries with values not equal to the specified value'
    )
    between = FilterDetails(
        name='between',
        value_type=Tuple[int, int], 
        django_lookup='range',
        description='Filter for entries with values between two specified values (inclusive)'
    )
    valueExists = FilterDetails(
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
    """
    An enumerationclass containing filter details for float field values.
    """
    lessThan = FilterDetails(
        name='lessThan',
        value_type=float, 
        django_lookup='lt',
        description='Filter for entries with values less than the specified value'
    )
    lessThanOrEqual = FilterDetails(
        name='lessThanOrEqual',
        value_type=float, 
        django_lookup='lte',
        description='Filter for entries with values less than or equal to the specified value'
    )
    greaterThan = FilterDetails(
        name='greaterThan',
        value_type=float, 
        django_lookup='gt',
        description='Filter for entries with values greater than the specified value'
    )
    greaterThanOrEqual = FilterDetails(
        name='greaterThanOrEqual',
        value_type=float,  
        django_lookup='gte',
        description='Filter for entries with values greater than or equal to the specified value'
    )
    equal = FilterDetails(
        name='equal',
        value_type=float, 
        django_lookup='exact',
        description='Filter for entries with values exactly equal to the specified value'
    )
    notEqual = equal.invert_logic(
        name='not.equal',
        description='Filter for entries with values not equal to the specified value'
    )
    between = FilterDetails(
        name='between',
        value_type=Tuple[float, float], 
        django_lookup='range',
        description='Filter for entries with values between two specified values (inclusive)'
    )
    valueExists = FilterDetails(
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
    """
    An enumerationclass containing filter details for boolean field values.
    """
    equals = FilterDetails(
        name='',
        value_type = bool, 
        django_lookup = 'equals',
        description = 'Filter for yes/no statement',
    )
    
    
class ReferenceFilters(FilterEnum):
    """
    An enumerationclass containing filter details for reference field values.
    """
    equals = FilterDetails(
        name='',
        value_type = str, 
        django_lookup = 'equals',
        description = 'Filter for a matching reference Id',
    )
    notEquals = equals.invert_logic(
        name='not.equals',
        description = 'Filter for a mismatching reference Id',
    )
    oneOf = FilterDetails(
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
    """
    An enumerationclass containing filter details for coded concept field values.
    """
    codeEquals = FilterDetails(
        name='code',
        value_type = str, 
        django_lookup = 'code',
        description = 'Filter for a matching code',
    )
    codeIncludes = FilterDetails(
        name='code.includes',
        value_type = List[str], 
        django_lookup = 'code__in',
        description = 'Filter for a matching set of codes',
    )
    codeContains = FilterDetails(
        name='code.contains',
        value_type = List[str], 
        django_lookup = 'code__in',
        description = 'Filter for partially matching codes',
    )
    displayEquals = FilterDetails(
        name='display',
        value_type = str, 
        django_lookup = 'display',
        description = 'Filter for a fully matching concept text',
    )
    displayContains = FilterDetails(
        name='display.contains',
        value_type = str, 
        django_lookup = 'display__icontains',
        description = 'Filter for a partially matching concept text',
    )
    codeDescendsFrom = FilterDetails(
        name='code.descendsFrom',
        value_type = List[str], 
        django_lookup = 'descendsfrom__code',
        description = 'Filter for all child concept of a given code',
    )
    