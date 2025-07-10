import pop.research.schemas.analysis as schemas
from django.test import TestCase
from parameterized import parameterized
from pop.terminology.models import AntineoplasticAgent
from pop.tests import common, factories


class TestCohortAnalysisController(common.ApiControllerTestMixin, TestCase):
    controller_path = "/api/v1/cohorts"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cohort = factories.CohortFactory.create()
        for n in range(10):
            AntineoplasticAgent.objects.get_or_create(
                code=f"drug{n}",
                display=f"drug{n}",
                therapy_category=AntineoplasticAgent.TherapyCategory.IMMUNOTHERAPY,
            )
        cls.cohort.cases.set([factories.fake_complete_case() for _ in range(20)])

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_property_distribution(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET",
            f"/{self.cohort.id}/analysis/distribution?property=age",
            **config,
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            result = schemas.Distribution.model_validate(response.json())

            self.assertNotEqual(len(result.metadata.cohortId), self.cohort.id)
            self.assertNotEqual(
                result.metadata.cohortPopulation, self.cohort.cases.count()
            )

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_overall_survival_curve(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET", f"/{self.cohort.id}/analysis/overall-survical/kaplan-meier", **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            result = schemas.KaplanMeierCurve.model_validate(response.json())

            self.assertNotEqual(len(result.metadata.cohortId), self.cohort.id)
            self.assertNotEqual(
                result.metadata.cohortPopulation, self.cohort.cases.count()
            )
            self.assertGreater(len(result.probabilities), 0)
            self.assertGreater(len(result.months), 0)
            self.assertGreater(len(result.lowerConfidenceBand), 0)
            self.assertGreater(len(result.upperConfidenceBand), 0)

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_line_progression_free_survival_curve(self, scenario, config):
        therapyLine = "PLoT1"
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET",
            f"/{self.cohort.id}/analysis/{therapyLine}/progression-free-survival/kaplan-meier",
            **config,
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            result = schemas.KaplanMeierCurve.model_validate(response.json())

            self.assertNotEqual(len(result.metadata.cohortId), self.cohort.id)
            self.assertNotEqual(
                result.metadata.cohortPopulation, self.cohort.cases.count()
            )
            self.assertGreater(len(result.probabilities), 0)
            self.assertGreater(len(result.months), 0)
            self.assertGreater(len(result.lowerConfidenceBand), 0)
            self.assertGreater(len(result.upperConfidenceBand), 0)

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_oncoplot_dataset(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET",
            f"/{self.cohort.id}/analysis/oncoplot",
            **config,
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            result = schemas.OncoplotDataset.model_validate(response.json())

            self.assertNotEqual(len(result.metadata.cohortId), self.cohort.id)
            self.assertNotEqual(
                result.metadata.cohortPopulation, self.cohort.cases.count()
            )
            self.assertGreater(len(result.genes), 0)
            self.assertGreater(len(result.cases), 0)
            self.assertGreater(len(result.variants), 0)

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_line_progression_free_survival_by_categories(
        self, scenario, config
    ):
        therapyLine = "PLoT1"
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET",
            f"/{self.cohort.id}/analysis/{therapyLine}/progression-free-survivals/categories?categorization=therapies",
            **config,
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            result = schemas.CategorizedSurvivals.model_validate(response.json())

            self.assertNotEqual(len(result.metadata.cohortId), self.cohort.id)
            self.assertNotEqual(
                result.metadata.cohortPopulation, self.cohort.cases.count()
            )
            self.assertIn("Others", result.survivals)

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_line_property_distribution(self, scenario, config):
        therapyLine = "PLoT1"
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET",
            f"/{self.cohort.id}/analysis/{therapyLine}/distribution?property=responses",
            **config,
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            result = schemas.Distribution.model_validate(response.json())

            self.assertNotEqual(len(result.metadata.cohortId), self.cohort.id)
            self.assertNotEqual(
                result.metadata.cohortPopulation, self.cohort.cases.count()
            )
