import pytest

from django.test import TestCase
from django.db.models import F

from pop.terminology.models import AntineoplasticAgent
from pop.tests import factories
from pop.research.analysis import (
    calculate_pfs_by_combination_therapy,
    calculate_Kappler_Maier_survival_curve,
    get_progression_free_survival_for_therapy_line,
    calculate_pfs_by_therapy_classification,
)
from unittest.mock import MagicMock, patch


class TestKapplerMeierCurves(TestCase):

    def _assert_correct_KM_Curve(self):
        survival_axis, survival_prob, ci95 = calculate_Kappler_Maier_survival_curve(
            self.survival_months
        )
        self.assertEqual(survival_axis, self.expected_survival_axis)

        for value, expected in zip(survival_prob, self.expected_survival_prob):
            self.assertAlmostEqual(value, expected, places=5)

        if self.expected_ci:
            for lower_ci, expected in zip(ci95["lower"], self.expected_ci["lower"]):
                self.assertAlmostEqual(lower_ci, expected, places=2)
            for upper_ci, expected in zip(ci95["upper"], self.expected_ci["upper"]):
                self.assertAlmostEqual(upper_ci, expected, places=2)

    def test_empty_dataset_raises_error(self):
        self.survival_months = []
        with pytest.raises(ValueError):
            self._assert_correct_KM_Curve()

    def test_ignores_none_values(self):
        self.survival_months = [1, 2, 2, 3, None, 3, 3, None, 4, 5]
        self.expected_survival_axis = [0, 1, 2, 3, 4, 5]
        self.expected_survival_prob = [1.0, 0.875, 0.625, 0.25, 0.125, 0.0]
        self.expected_ci = {
            "lower": [1, 0.387, 0.229, 0.037, 0.006, 0],
            "upper": [1, 0.981, 0.861, 0.558, 0.423, 0],
        }
        self._assert_correct_KM_Curve()

    def test_basic_small_dataset(self):
        self.survival_months = [1, 2, 2, 3, 3, 3, 4, 5]
        self.expected_survival_axis = [0, 1, 2, 3, 4, 5]
        self.expected_survival_prob = [1.0, 0.875, 0.625, 0.25, 0.125, 0.0]
        self.expected_ci = {
            "lower": [1, 0.387, 0.229, 0.037, 0.006, 0],
            "upper": [1, 0.981, 0.861, 0.558, 0.423, 0],
        }
        self._assert_correct_KM_Curve()

    def test_non_integer_survivals(self):
        self.survival_months = [1.1, 2.2, 2.3, 3.4, 3.2, 3.2, 4.1, 5.0]
        self.expected_survival_axis = [0, 1, 2, 3, 4, 5]
        self.expected_survival_prob = [1.0, 0.875, 0.625, 0.25, 0.125, 0.0]
        self.expected_ci = None
        self._assert_correct_KM_Curve()

    def test_no_censored_data(self):
        self.survival_months = [1, 2, 3, 4, 5]
        self.expected_survival_axis = [0, 1, 2, 3, 4, 5]
        self.expected_survival_prob = [1.0, 0.8, 0.6, 0.4, 0.2, 0.0]
        self.expected_ci = None
        self._assert_correct_KM_Curve()

    def test_long_term_survivors(self):
        self.survival_months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.expected_survival_axis = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.expected_survival_prob = [
            1,
            0.9,
            0.8,
            0.7,
            0.6,
            0.5,
            0.4,
            0.3,
            0.2,
            0.1,
            0.0,
        ]
        self.expected_ci = None
        self._assert_correct_KM_Curve()


class TestGetProgressionFreeSurvivalForTherapyLine(TestCase):

    @staticmethod
    def _simulate_case():
        user = factories.UserFactory.create()
        case = factories.PatientCaseFactory.create()
        therapy_line_1 = factories.TherapyLineFactory.create(
            case=case, intent="curative", ordinal=1
        )
        systemic_therapy_1 = factories.SystemicTherapyFactory.create(
            case=case, therapy_line=therapy_line_1
        )
        factories.SystemicTherapyMedicationFactory.create(
            systemic_therapy=systemic_therapy_1
        )
        factories.SystemicTherapyMedicationFactory.create(
            systemic_therapy=systemic_therapy_1
        )
        therapy_line_2 = factories.TherapyLineFactory.create(
            case=case, intent="palliative", ordinal=1
        )
        systemic_therapy_2 = factories.SystemicTherapyFactory.create(
            case=case, therapy_line=therapy_line_2
        )
        factories.SystemicTherapyMedicationFactory.create(
            systemic_therapy=systemic_therapy_2
        )
        factories.SystemicTherapyMedicationFactory.create(
            systemic_therapy=systemic_therapy_2
        )
        return case

    @classmethod
    def setUpTestData(cls):
        cls.cohort = factories.CohortFactory()
        cls.case1 = cls._simulate_case()
        cls.case2 = cls._simulate_case()
        cls.case3 = cls._simulate_case()
        cls.cohort.cases.set([cls.case1, cls.case2, cls.case3])
        cls.exected = [
            pfs
            for case in [cls.case1, cls.case2, cls.case3]
            for pfs in list(
                case.therapy_lines.filter(intent="curative")
                .annotate(pfs=F("progression_free_survival"))
                .values_list("pfs", flat=True)
            )
        ]

    def test_get_pfs_incuding_CLoT1_lines(self):
        result = get_progression_free_survival_for_therapy_line(
            self.cohort,
            intent="curative",
            ordinal=1,
        )
        self.assertEqual(sorted(self.exected), sorted(result))

    def test_get_pfs_excluding_PLoT1_lines(self):
        result = get_progression_free_survival_for_therapy_line(
            self.cohort,
            exclude_filters=dict(intent="palliative", ordinal=1),
        )
        self.assertEqual(sorted(self.exected), sorted(result))

    def test_get_pfs_by_therapy(self):
        result = calculate_pfs_by_combination_therapy(self.cohort, "CLoT1")
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(self.exected), sorted(list(result.values())[0]))
        self.assertEqual([], result["Others"])


class TestCalculatePFSByTherapyClassification(TestCase):

    @staticmethod
    def _simulate_case():
        user = factories.UserFactory.create()
        case = factories.PatientCaseFactory.create()
        therapy_line_1 = factories.TherapyLineFactory.create(
            case=case, intent="curative", ordinal=1
        )
        systemic_therapy_1 = factories.SystemicTherapyFactory.create(
            case=case, therapy_line=therapy_line_1
        )
        factories.SystemicTherapyMedicationFactory.create(
            systemic_therapy=systemic_therapy_1,
            drug=AntineoplasticAgent.objects.get_or_create(
                code="drug1",
                display="drug1",
                therapy_category=AntineoplasticAgent.TherapyCategory.CHEMOTHERAPY,
            )[0],
        )
        factories.SystemicTherapyMedicationFactory.create(
            systemic_therapy=systemic_therapy_1,
            drug=AntineoplasticAgent.objects.get_or_create(
                code="drug2",
                display="drug2",
                therapy_category=AntineoplasticAgent.TherapyCategory.IMMUNOTHERAPY,
            )[0],
        )
        therapy_line_2 = factories.TherapyLineFactory.create(
            case=case, intent="palliative", ordinal=1
        )
        systemic_therapy_2 = factories.SystemicTherapyFactory.create(
            case=case, therapy_line=therapy_line_2
        )
        factories.SystemicTherapyMedicationFactory.create(
            systemic_therapy=systemic_therapy_2,
            drug=AntineoplasticAgent.objects.get_or_create(
                code="drug1",
                display="drug1",
                therapy_category=AntineoplasticAgent.TherapyCategory.CHEMOTHERAPY,
            )[0],
        )
        factories.RadiotherapyFactory.create(case=case, therapy_line=therapy_line_2)
        return case

    @classmethod
    def setUpTestData(cls):
        cls.cohort = factories.CohortFactory.create()
        cls.case1 = cls._simulate_case()
        cls.case2 = cls._simulate_case()
        cls.case3 = cls._simulate_case()
        cls.cohort.cases.set([cls.case1, cls.case2, cls.case3])
        cls.expected = [
            pfs
            for case in [cls.case1, cls.case2, cls.case3]
            for pfs in list(
                case.therapy_lines.filter(intent="curative")
                .annotate(pfs=F("progression_free_survival"))
                .values_list("pfs", flat=True)
            )
        ]

    def test_get_pfs_incuding_CLoT1_lines(self):
        result = calculate_pfs_by_therapy_classification(self.cohort, "CLoT1")
        self.assertEqual(sorted(self.expected), sorted(result["Chemoimmunotherapy"]))

    def test_with_no_cases(self):
        self.cohort.cases.clear()
        result = calculate_pfs_by_therapy_classification(self.cohort, "CLoT1")
        self.assertEqual([], result["Others"])
