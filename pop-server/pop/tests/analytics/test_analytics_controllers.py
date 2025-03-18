from pop.tests.oncology.test_oncology_controllers import ApiControllerTextMixin
from django.test import TestCase
from pop.analytics import schemas, models
from pop.tests import factories, common
from parameterized import parameterized    
import numpy as np

class TestCohortController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/cohorts'
    FACTORY = factories.CohortFactory
    MODEL = models.Cohort
    SCHEMA = schemas.CohortSchema
    CREATE_SCHEMA = schemas.CohortCreateSchema             


class TestCohortTraitsController(common.ApiControllerTestMixin, TestCase):
    controller_path = '/api/cohorts'

    @classmethod 
    def setUpTestData(cls):
        super().setUpTestData()
        cls.trait = 'age'
        cls.cohort = factories.CohortFactory.create()
        cls.cohort.cases.set([factories.PatientCaseFactory.create() for _ in range(10)])

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_trait_average(self, scenario, config):        
        # Call the API endpoint
        response = self.call_api_endpoint('GET', f'/{self.cohort.id}/traits/{self.trait}/average', **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 200)
            values = [getattr(case, self.trait) for case in self.cohort.cases.all()]
            expected = schemas.cohort.CohortTraitAverage(average=np.average(values), standardDeviation=np.std(values)).model_dump()
            result = schemas.cohort.CohortTraitAverage.model_validate(response.json()).model_dump()
            self.assertDictEqual(result, expected)
    
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_trait_median(self, scenario, config):        
        # Call the API endpoint        
        response = self.call_api_endpoint('GET', f'/{self.cohort.id}/traits/{self.trait}/median', **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 200)
            values = [getattr(case, self.trait) for case in self.cohort.cases.all()]
            expected = schemas.cohort.CohortTraitMedian(median=np.percentile(values, 50), interQuartalRange=(np.percentile(values, 25), np.percentile(values, 75))).model_dump()
            result = schemas.cohort.CohortTraitMedian.model_validate(response.json()).model_dump()
            self.assertDictEqual(result, expected)



class TestDatasetController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/datasets'
    FACTORY = factories.DatasetFactory
    MODEL = models.Dataset
    SCHEMA = schemas.Dataset
    CREATE_SCHEMA = schemas.DatasetCreate             
