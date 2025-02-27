
from django.test import TestCase
from django.db.models import F 

import numpy as np 

from pop.tests import factories
from pop.analytics.analysis import calculate_pfs_by_combination_therapy, calculate_Kappler_Maier_survival_curve, get_progression_free_survival_for_therapy_line

class TestKapplerMeierCurves(TestCase):

    def _assert_correct_KM_Curve(self):
        survival_axis, survival_prob, ci95 = calculate_Kappler_Maier_survival_curve(self.survival_months)       
        self.assertEqual(survival_axis, self.expected_survival_axis)
        np.testing.assert_almost_equal(survival_prob, self.expected_survival_prob, 5)
        if self.expected_ci:
            np.testing.assert_almost_equal(ci95['lower'], self.expected_ci['lower'], 2)
            np.testing.assert_almost_equal(ci95['upper'], self.expected_ci['upper'], 2)

    def test_basic_small_dataset(self):
        self.survival_months = [1, 2, 2, 3, 3, 3, 4, 5]
        self.expected_survival_axis = [0, 1, 2, 3, 4, 5]
        self.expected_survival_prob = [1.0, 0.875, 0.625, 0.25, 0.125, 0.0]
        self.expected_ci = {
            "lower": [1, 0.387, 0.229, 0.037, 0.006, 0], 
            "upper": [1, 0.981, 0.861, 0.558, 0.423, 0]
        }
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
        self.expected_survival_prob = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0. ]
        self.expected_ci = None
        self._assert_correct_KM_Curve()


class TestGetProgressionFreeSurvivalForTherapyLine(TestCase):
    
    def _simulate_case(self):
        user = factories.UserFactory.create()
        case = factories.PatientCaseFactory.create(created_by=user)
        therapy_line_1 = factories.TherapyLineFactory.create(case=case, intent='curative', ordinal=1, created_by=user)
        systemic_therapy_1 = factories.SystemicTherapyFactory.create(case=case, therapy_line=therapy_line_1,created_by=user)
        factories.SystemicTherapyMedicationFactory.create(systemic_therapy=systemic_therapy_1, created_by=user)
        factories.SystemicTherapyMedicationFactory.create(systemic_therapy=systemic_therapy_1, created_by=user)
        therapy_line_2 = factories.TherapyLineFactory.create(case=case, intent='palliative', ordinal=1, created_by=user)
        systemic_therapy_2 = factories.SystemicTherapyFactory.create(case=case, therapy_line=therapy_line_2, created_by=user)
        factories.SystemicTherapyMedicationFactory.create(systemic_therapy=systemic_therapy_2, created_by=user)
        factories.SystemicTherapyMedicationFactory.create(systemic_therapy=systemic_therapy_2, created_by=user)
        return case 
    
    def setUp(self):
        self.cohort = factories.CohortFactory()
        self.case1 = self._simulate_case()
        self.case2 = self._simulate_case()
        self.case3 = self._simulate_case()
        self.cohort.cases.set([self.case1, self.case2, self.case3])
        self.exected = [
            pfs for case in [self.case1, self.case2, self.case3] 
                for pfs in list(case.therapy_lines.filter(intent='curative').annotate(pfs=F('progression_free_survival')).values_list('pfs', flat=True)) 
        ]
        
    def test_get_pfs_incuding_CLoT1_lines(self):
        result = get_progression_free_survival_for_therapy_line(self.cohort, 
            intent='curative', ordinal=1,
        )
        self.assertEqual(sorted(self.exected), sorted(result))
        
    def test_get_pfs_excluding_PLoT1_lines(self):
        result = get_progression_free_survival_for_therapy_line(self.cohort, 
            exclude_filters=dict(intent='palliative', ordinal=1),
        )
        self.assertEqual(sorted(self.exected), sorted(result))
        
    
    def test_get_pfs_by_therapy(self):
        result = calculate_pfs_by_combination_therapy(self.cohort, 'CLoT1')
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(self.exected), sorted(list(result.values())[0]))
        self.assertEqual([], result['Others'])
        