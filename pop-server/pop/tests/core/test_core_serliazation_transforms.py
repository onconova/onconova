from django.test import TestCase
from parameterized import parameterized
from datetime import datetime

from pop.tests.models import MockModel, OptionsEnum, MockCodedConcept
import pop.core.serialization.transforms as t


class TestDjangoTransforms(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        conceptA, _ = MockCodedConcept.objects.get_or_create(
            code="code-A", display="concept-A", system="code-system-A"
        )
        conceptB, _ = MockCodedConcept.objects.get_or_create(
            code="code-B", display="concept-B", system="code-system-B"
        )
        cls.instanceA = MockModel.objects.create(
            id="instanceA",
            str_field="this_string_is_version_A",
            date_field=datetime(2000, 1, 1),
            int_field=2,
            float_field=2.5,
            enum_field=OptionsEnum.OPTIONA,
            bool_field=True,
            period_field=(datetime(2000, 1, 1).date(), datetime(2009, 12, 12).date()),
            coded_concept_field=conceptA,
        )
        cls.instanceA.multi_coded_concept_field.set([conceptA, conceptB])

    @staticmethod
    def parameterized_filter_test_name(fcn, idx, param):
        return f"{fcn.__name__}_{idx}_{list(param)[0][0].__name__}"

    def assert_transformation(self, field, TransformationClass, value, expected):
        expression = TransformationClass.generate_annotation_expression(field, value)
        filtered_queryset = MockModel.objects.annotate(transform=expression)
        value = filtered_queryset.values("transform").first()
        self.assertEqual(
            value["transform"],
            expected,
            "Transform failed to yield the correct annotation in the queryset.",
        )

    @parameterized.expand(
        [
            (t.GetCodedConceptDisplay, None, "concept-A"),
            (t.GetCodedConceptCode, None, "code-A"),
            (t.GetCodedConceptSystem, None, "code-system-A"),
        ],
        name_func=parameterized_filter_test_name,
    )
    def test_coded_concept_filtering(self, TransformationClass, value, expected):
        self.assert_transformation(
            "coded_concept_field", TransformationClass, value, expected
        )
