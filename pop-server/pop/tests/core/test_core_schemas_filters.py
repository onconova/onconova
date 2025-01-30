from django.db.models import Avg, Q
from django_mock_queries.query import MockSet, MockModel
from django.test import TestCase
from parameterized import parameterized
from datetime import datetime

from unittest.mock import MagicMock
from enum import Enum
from django.db.backends.postgresql.psycopg_any import DateRange
from pop.terminology.models import AdministrativeGender as TestCodedConcept
from pop.core.schemas.filters import *

class OptionsEnum(Enum):
    OPTIONA = 'optionA'
    OPTIONB = 'optionB'

instanceA = MockModel(
    mock_name='instanceA', 
    str_field='this_string_is_version_A', 
    nullable_field=None,
    date_field=datetime(2000,1,1),
    int_field=2,
    float_field=2.5,
    enum_field=OptionsEnum.OPTIONA,
    bool_field=True,
    period_field=(date(2000,1,1), date(2009,12,12)),
)
instanceB = MockModel(
    mock_name='instanceB', 
    str_field='another_string_is_version_B', 
    nullable_field='not_null',
    date_field=datetime(2020,1,1),
    int_field=5,
    float_field=5.5,
    enum_field=OptionsEnum.OPTIONB,
    bool_field=False,
    period_field=(date(2010,1,1), date(2020,1,1)),
)
test_queryset = MockSet(
    instanceA,
    instanceB,
)


class TestDjangoFilters(TestCase):

    @staticmethod
    def parameterized_filter_test_name(fcn,idx,param):
        return f'{fcn.__name__}_{idx}_{list(param)[0][0].__name__}'


    def assert_filtering(self, field, FilterClass, value, expected):
        schema = MagicMock()
        schema._queryset_model._meta.get_field.return_value.related_model = TestCodedConcept
        query = FilterClass.generate_query_expression(field)(schema, value)
        filtered_queryset = test_queryset.filter(query)
        self.assertTrue(filtered_queryset.count() == 1, 'Filter failed to limit the queryset to a single result (multiple found).')
        self.assertEqual(filtered_queryset.first(), expected, 'Filter failed to match the correct entry in the queryset.')


    @parameterized.expand(
        [
           (ExactStringFilter, 'this_string_is_version_A', instanceA),
           (NotExactStringFilter, 'this_string_is_version_A', instanceB),
           (ContainsStringFilter, 'this', instanceA),
           (NotContainsStringFilter, 'this', instanceB),
           (BeginsWithStringFilter, 'this_', instanceA),
           (NotBeginsWithStringFilter, 'this_', instanceB),
           (EndsWithStringFilter, 'version_A', instanceA),
           (NotEndsWithStringFilter, '_version_A', instanceB),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_string_filtering(self, FilterClass, value, expected):
        self.assert_filtering('str_field', FilterClass, value, expected)


    @parameterized.expand(
        [
           (IsNullFilter, True, instanceA),
           (NotIsNullFilter, False, instanceA),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_null_filtering(self, FilterClass, value, expected):
        self.assert_filtering('nullable_field', FilterClass, value, expected)


    @parameterized.expand(
        [
           (BeforeDateFilter, datetime(2010,1,1), instanceA),
           (AfterDateFilter, datetime(2010,1,1), instanceB),
           (OnOrBeforeDateFilter, datetime(2010,1,1), instanceA),
           (OnOrAfterDateFilter, datetime(2010,1,1), instanceB),
           (OnDateFilter, datetime(2000,1,1), instanceA),
           (NotOnDateFilter, datetime(2000,1,1), instanceB),
           (BetweenDatesFilter, [datetime(1999,1,1), datetime(2001,1,1)], instanceA),
           (NotBetweenDatesFilter, [datetime(1999,1,1), datetime(2001,1,1)], instanceB),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_date_filtering(self, FilterClass, value, expected):
        self.assert_filtering('date_field', FilterClass, value, expected)

    @parameterized.expand(
        [
           (LessThanIntegerFilter, 3, instanceA),
           (LessThanOrEqualIntegerFilter, 3, instanceA),
           (GreaterThanIntegerFilter, 3, instanceB),
           (GreaterThanOrEqualIntegerFilter, 3, instanceB),
           (EqualIntegerFilter, 2, instanceA),
           (NotEqualIntegerFilter, 2, instanceB),
           (BetweenIntegerFilter, [0,4], instanceA),
           (NotBetweenIntegerFilter, [0,4], instanceB),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_int_filtering(self, FilterClass, value, expected):
        self.assert_filtering('int_field', FilterClass, value, expected)

    @parameterized.expand(
        [
           (LessThanFloatFilter, 3.0, instanceA),
           (LessThanOrEqualFloatFilter, 3.0, instanceA),
           (GreaterThanFloatFilter, 3.0, instanceB),
           (GreaterThanOrEqualFloatFilter, 3.0, instanceB),
           (EqualFloatFilter, 2.5, instanceA),
           (NotEqualFloatFilter, 2.5, instanceB),
           (BetweenFloatFilter, [0.0,4.0], instanceA),
           (NotBetweenFloatFilter, [0.0,4.0], instanceB),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_float_filtering(self, FilterClass, value, expected):
        self.assert_filtering('float_field', FilterClass, value, expected)

    @parameterized.expand(
        [
           (EqualsEnumFilter, OptionsEnum.OPTIONA, instanceA),
           (NotEqualsEnumFilter, OptionsEnum.OPTIONA, instanceB),
           (AnyOfEnumFilter, [OptionsEnum.OPTIONA], instanceA),
           (NotAnyOfEnumFilter, [OptionsEnum.OPTIONA], instanceB),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_enum_filtering(self, FilterClass, value, expected):
        self.assert_filtering('enum_field', FilterClass, value, expected)


    @parameterized.expand(
        [
           (EqualsBooleanFilter, True, instanceA),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_bool_filtering(self, FilterClass, value, expected):
        self.assert_filtering('bool_field', FilterClass, value, expected)


    @parameterized.expand(
        [
           (EqualsConceptFilter, 'code-A', instanceA),
           (NotEqualsConceptFilter, 'code-A', instanceB),
           (AnyOfConceptFilter, ['code-A', 'code-C'], instanceA),
           (NotAnyOfConceptFilter, ['code-A', 'code-C'], instanceB),
           (DescendantsOfConceptFilter, 'parent-A', instanceA),
           (DescendantsOfConceptFilter, 'grandparent-A', instanceA),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_coded_concept_filtering(self, FilterClass, value, expected):
        grandparentA,_ = TestCodedConcept.objects.get_or_create(code='grandparent-A', display='grandparent A')
        parentA,_ = TestCodedConcept.objects.get_or_create(code='parent-A', display='parent A', parent=grandparentA)
        conceptA,_ = TestCodedConcept.objects.get_or_create(code='code-A', display='concept A', parent=parentA)
        parentB,_ = TestCodedConcept.objects.get_or_create(code='parent-B', display='parent B')
        conceptB,_ = TestCodedConcept.objects.get_or_create(code='code-B', display='concept B', parent=parentB)
        instanceA.coded_concept_field = conceptA
        instanceB.coded_concept_field = conceptB
        self.assert_filtering('coded_concept_field', FilterClass, value, expected)


    @parameterized.expand(
        [
           (OverlapsPeriodFilter, (date(2000,1,1), date(2009,12,12)), instanceA),
           (NotOverlapsPeriodFilter, (date(2000,1,1), date(2009,12,12)), instanceB),
           (ContainsPeriodFilter, (date(2000,1,1), date(2009,12,12)), instanceA),
           (NotContainsPeriodFilter, (date(2000,1,1), date(2009,12,12)), instanceB),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_period_filtering(self, FilterClass, value, expected):
        self.assert_filtering('period_field', FilterClass, value, expected)
