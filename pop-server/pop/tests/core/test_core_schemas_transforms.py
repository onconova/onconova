from django.db.models import Avg, Q
from django_mock_queries.query import MockSet, MockModel
from django.test import TestCase
from parameterized import parameterized
from datetime import datetime

from unittest.mock import MagicMock
from enum import Enum
from pop.terminology.models import AdministrativeGender as TestCodedConcept
import pop.core.transforms as t

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
    period_field=(datetime(2000,1,1), datetime(2009,12,12)),
)
test_queryset = MockSet(instanceA,)


class TestDjangoTransforms(TestCase):

    @staticmethod
    def parameterized_filter_test_name(fcn,idx,param):
        return f'{fcn.__name__}_{idx}_{list(param)[0][0].__name__}'


    def assert_transformation(self, field, TransformationClass, value, expected):
        expression = TransformationClass.generate_annotation_expression(field, value)
        filtered_queryset = test_queryset.annotate(transform = expression)
        value = filtered_queryset.values('transform').first()
        self.assertEqual(value['transform'], expected, 'Transform failed to yield the correct annotation in the queryset.')


    @parameterized.expand(
        [
           (t.GetCodedConceptDisplay, None, 'concept-A'),
           (t.GetCodedConceptCode, None, 'code-A'),
           (t.GetCodedConceptSystem, None, 'code-system-A'),
        ],
        name_func = parameterized_filter_test_name
    )
    def test_coded_concept_filtering(self, TransformationClass, value, expected):
        instanceA.coded_concept_field = TestCodedConcept.objects.get_or_create(code='code-A', display='concept-A', system='code-system-A')
        self.assert_transformation('coded_concept_field', TransformationClass, value, expected)

