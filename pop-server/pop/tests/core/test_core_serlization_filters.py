from django.test import TestCase
from parameterized import parameterized
from datetime import datetime

from unittest.mock import MagicMock
from pop.tests.models import MockModel, OptionsEnum, MockCodedConcept
import pop.core.serialization.filters as f

class TestDjangoFilters(TestCase):

    @classmethod 
    def setUpTestData(cls):
        super().setUpTestData()
        
        grandparentA,_ = MockCodedConcept.objects.get_or_create(code='grandparent-A', display='grandparent A')
        parentA,_ = MockCodedConcept.objects.get_or_create(code='parent-A', display='parent A', parent=grandparentA)
        conceptA,_ = MockCodedConcept.objects.get_or_create(code='code-A', display='concept A', parent=parentA)
        parentB,_ = MockCodedConcept.objects.get_or_create(code='parent-B', display='parent B')
        conceptB,_ = MockCodedConcept.objects.get_or_create(code='code-B', display='concept B', parent=parentB)

        cls.conceptA1,_ = MockCodedConcept.objects.get_or_create(code='code-A-1', display='concept A1', parent=parentA)
        cls.conceptA2,_ = MockCodedConcept.objects.get_or_create(code='code-A-2', display='concept A2', parent=parentA)
        cls.conceptB1,_ = MockCodedConcept.objects.get_or_create(code='code-B-1', display='concept B1', parent=parentB)
        cls.conceptB2,_ = MockCodedConcept.objects.get_or_create(code='code-B-2', display='concept B2', parent=parentB)
        
        cls.instanceA = MockModel.objects.create(
            id='instanceA',
            str_field='this_string_is_version_A', 
            date_field=datetime(2000,1,1),
            int_field=2,
            float_field=2.5,
            enum_field=OptionsEnum.OPTIONA,
            bool_field=True,
            period_field=(datetime(2000,1,1).date(), datetime(2009,12,12).date()),
            coded_concept_field=conceptA,
        )
        cls.instanceA.multi_coded_concept_field.set([cls.conceptA1, cls.conceptA2])
        
        cls.instanceB = MockModel.objects.create(
            id='instanceB',
            str_field='another_string_is_version_B', 
            date_field=datetime(2020,1,1),
            int_field=5,
            float_field=5.5,
            enum_field=OptionsEnum.OPTIONB,
            bool_field=False,
            period_field=(datetime(2010,1,1).date(), datetime(2020,1,1).date()),
            coded_concept_field=conceptB,
        )
        cls.instanceB.multi_coded_concept_field.set([cls.conceptB1, cls.conceptB2])

        

    @staticmethod
    def parameterized_filter_test_name(fcn,idx,param):
        return f'{fcn.__name__}_{idx}_{list(param)[0][0].__name__}'

    def assert_filtering(self, field, FilterClass, value, expected):
        schema = MagicMock()
        schema._queryset_model = MockModel
        query = FilterClass.generate_query_expression(field)(schema, value)
        filtered_queryset = MockModel.objects.filter(query).distinct()
        self.assertTrue(filtered_queryset.count() > 0, 'Filter resulted in an empty queryset.')
        self.assertTrue(filtered_queryset.count() == 1, 'Filter failed to limit the queryset to a single result (multiple found).')
        self.assertEqual(filtered_queryset.first().pk, expected, 'Filter failed to match the correct entry in the queryset.')


    @parameterized.expand(
        [
           (f.ExactStringFilter, 'this_string_is_version_A', 'instanceA'),
           (f.NotExactStringFilter, 'this_string_is_version_A', 'instanceB'),
           (f.ContainsStringFilter, 'this', 'instanceA'),
           (f.NotContainsStringFilter, 'this','instanceB'),
           (f.BeginsWithStringFilter, 'this_', 'instanceA'),
           (f.NotBeginsWithStringFilter, 'this_', 'instanceB'),
           (f.EndsWithStringFilter, 'version_A', 'instanceA'),
           (f.NotEndsWithStringFilter, '_version_A', 'instanceB'),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_string_filtering(self, FilterClass, value, expected):
        self.assert_filtering('str_field', FilterClass, value, expected)

    @parameterized.expand(
        [
           (f.BeforeDateFilter, datetime(2010,1,1), 'instanceA'),
           (f.AfterDateFilter, datetime(2010,1,1), 'instanceB'),
           (f.OnOrBeforeDateFilter, datetime(2010,1,1), 'instanceA'),
           (f.OnOrAfterDateFilter, datetime(2010,1,1), 'instanceB'),
           (f.OnDateFilter, datetime(2000,1,1), 'instanceA'),
           (f.NotOnDateFilter, datetime(2000,1,1), 'instanceB'),
           (f.BetweenDatesFilter, [datetime(1999,1,1), datetime(2001,1,1)], 'instanceA'),
           (f.NotBetweenDatesFilter, [datetime(1999,1,1), datetime(2001,1,1)], 'instanceB'),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_date_filtering(self, FilterClass, value, expected):
        self.assert_filtering('date_field', FilterClass, value, expected)

    @parameterized.expand(
        [
           (f.LessThanIntegerFilter, 3, 'instanceA'),
           (f.LessThanOrEqualIntegerFilter, 3, 'instanceA'),
           (f.GreaterThanIntegerFilter, 3, 'instanceB'),
           (f.GreaterThanOrEqualIntegerFilter, 3, 'instanceB'),
           (f.EqualIntegerFilter, 2, 'instanceA'),
           (f.NotEqualIntegerFilter, 2, 'instanceB'),
           (f.BetweenIntegerFilter, [0,4], 'instanceA'),
           (f.NotBetweenIntegerFilter, [0,4], 'instanceB'),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_int_filtering(self, FilterClass, value, expected):
        self.assert_filtering('int_field', FilterClass, value, expected)

    @parameterized.expand(
        [
           (f.LessThanFloatFilter, 3.0, 'instanceA'),
           (f.LessThanOrEqualFloatFilter, 3.0, 'instanceA'),
           (f.GreaterThanFloatFilter, 3.0, 'instanceB'),
           (f.GreaterThanOrEqualFloatFilter, 3.0, 'instanceB'),
           (f.EqualFloatFilter, 2.5, 'instanceA'),
           (f.NotEqualFloatFilter, 2.5, 'instanceB'),
           (f.BetweenFloatFilter, [0.0,4.0], 'instanceA'),
           (f.NotBetweenFloatFilter, [0.0,4.0], 'instanceB'),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_float_filtering(self, FilterClass, value, expected):
        self.assert_filtering('float_field', FilterClass, value, expected)

    @parameterized.expand(
        [
           (f.EqualsEnumFilter, OptionsEnum.OPTIONA, 'instanceA'),
           (f.NotEqualsEnumFilter, OptionsEnum.OPTIONA, 'instanceB'),
           (f.AnyOfEnumFilter, [OptionsEnum.OPTIONA], 'instanceA'),
           (f.NotAnyOfEnumFilter, [OptionsEnum.OPTIONA], 'instanceB'),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_enum_filtering(self, FilterClass, value, expected):
        self.assert_filtering('enum_field', FilterClass, value, expected)


    @parameterized.expand(
        [
           (f.EqualsBooleanFilter, True, 'instanceA'),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_bool_filtering(self, FilterClass, value, expected):
        self.assert_filtering('bool_field', FilterClass, value, expected)


    @parameterized.expand(
        [
           (f.EqualsConceptFilter, 'code-A', 'instanceA'),
           (f.NotEqualsConceptFilter, 'code-A', 'instanceB'),
           (f.AnyOfConceptFilter, ['code-A', 'code-C'], 'instanceA'),
           (f.NotAnyOfConceptFilter, ['code-A', 'code-C'], 'instanceB'),
           (f.DescendantsOfConceptFilter, 'parent-A', 'instanceA'),
           (f.DescendantsOfConceptFilter, 'grandparent-A', 'instanceA'),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_coded_concept_filtering(self, FilterClass, value, expected):
        self.assert_filtering('coded_concept_field', FilterClass, value, expected)


    @parameterized.expand(
        [
           (f.EqualsConceptFilter, 'code-A-2', 'instanceA'),
           (f.NotEqualsConceptFilter, 'code-A-1', 'instanceB'),
           (f.AnyOfConceptFilter, ['code-A-2', 'code-C-1'], 'instanceA'),
           (f.NotAnyOfConceptFilter, ['code-A-1', 'code-A-2'], 'instanceB'),
           (f.DescendantsOfConceptFilter, 'parent-B', 'instanceB'),
           (f.AllOfConceptFilter, ['code-A-1', 'code-A-2'], 'instanceA'),
           (f.AllOfConceptFilter, ['code-A-1'], 'instanceC'),
           (f.NotAllOfConceptFilter, ['code-A-1', 'code-A-2'], 'instanceB'),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_multiple_coded_concept_filtering(self, FilterClass, value, expected):
        if FilterClass != f.NotAllOfConceptFilter:
            self.instanceC = MockModel.objects.create(id='instanceC')
            self.instanceC.multi_coded_concept_field.set([self.conceptA1])
        self.assert_filtering('multi_coded_concept_field', FilterClass, value, expected)
        

    @parameterized.expand(
        [
           (f.OverlapsPeriodFilter, (datetime(2000,1,1).date(), datetime(2009,12,12).date()), 'instanceA'),
           (f.NotOverlapsPeriodFilter, (datetime(2000,1,1).date(), datetime(2009,12,12).date()), 'instanceB'),
           (f.ContainsPeriodFilter, (datetime(2000,1,1).date(), datetime(2009,12,12).date()), 'instanceA'),
           (f.NotContainsPeriodFilter, (datetime(2000,1,1).date(), datetime(2009,12,12).date()), 'instanceB'),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_period_filtering(self, FilterClass, value, expected):
        self.assert_filtering('period_field', FilterClass, value, expected)
