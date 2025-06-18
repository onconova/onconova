from pop.tests.oncology.test_oncology_controllers import ApiControllerTextMixin
from django.test import TestCase
from pop.core.utils import average, std, percentile
from pop.research import models
from pop.research import schemas
from pop.tests import factories, common
from parameterized import parameterized
from collections import Counter


class TestCohortController(ApiControllerTextMixin, TestCase):
    controller_path = "/api/v1/cohorts"
    FACTORY = factories.CohortFactory
    MODEL = models.Cohort
    SCHEMA = schemas.CohortSchema
    CREATE_SCHEMA = schemas.CohortCreateSchema


class TestCohortTraitsController(common.ApiControllerTestMixin, TestCase):
    controller_path = "/api/v1/cohorts"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.trait = "age"
        cls.cohort = factories.CohortFactory.create()
        cls.cohort.cases.set([factories.PatientCaseFactory.create() for _ in range(10)])

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_trait_average(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET", f"/{self.cohort.id}/traits/{self.trait}/average", **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            values = [getattr(case, self.trait) for case in self.cohort.cases.all()]
            expected = schemas.cohort.CohortTraitAverage(
                average=average(values), standardDeviation=std(values)
            ).model_dump()
            result = schemas.cohort.CohortTraitAverage.model_validate(
                response.json()
            ).model_dump()
            self.assertDictEqual(result, expected)

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_trait_median(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET", f"/{self.cohort.id}/traits/{self.trait}/median", **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            values = [getattr(case, self.trait) for case in self.cohort.cases.all()]
            expected = schemas.cohort.CohortTraitMedian(
                median=percentile(values, 50),
                interQuartalRange=(percentile(values, 25), percentile(values, 75)),
            ).model_dump()
            result = schemas.cohort.CohortTraitMedian.model_validate(
                response.json()
            ).model_dump()
            self.assertDictEqual(result, expected)

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_cohort_trait_counts(self, scenario, config):
        self.trait = "gender.display"
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET", f"/{self.cohort.id}/traits/{self.trait}/counts", **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            counter = Counter([case.gender.display for case in self.cohort.cases.all()])
            expected = [
                schemas.cohort.CohortTraitCounts(
                    category=category,
                    counts=count,
                    percentage=round(count / self.cohort.cases.count() * 100, 4),
                ).model_dump()
                for category, count in counter.items()
            ]
            result = [
                schemas.cohort.CohortTraitCounts.model_validate(item).model_dump()
                for item in response.json()
            ]
            self.assertEqual(result, expected)


class TestDatasetController(ApiControllerTextMixin, TestCase):
    controller_path = "/api/v1/datasets"
    FACTORY = factories.DatasetFactory
    MODEL = models.Dataset
    SCHEMA = schemas.Dataset
    CREATE_SCHEMA = schemas.DatasetCreate


class TestProjectController(ApiControllerTextMixin, TestCase):
    controller_path = "/api/v1/projects"
    FACTORY = factories.ProjectFactory
    MODEL = models.Project
    SCHEMA = schemas.ProjectSchema
    CREATE_SCHEMA = schemas.ProjectCreateSchema


class TestProjectDataManagerController(ApiControllerTextMixin, TestCase):
    controller_path = "/api/v1/projects"
    FACTORY = factories.ProjectDataManagerGrantFactory
    MODEL = models.ProjectDataManagerGrant
    SCHEMA = schemas.ProjectDataManagerGrantSchema
    CREATE_SCHEMA = schemas.ProjectDataManagerGrantCreateSchema

    HAS_UPDATE_ENDPOINT = False

    def get_route_url(self, instance):
        return f"/{instance.project.id}/members/{instance.member.id}/data-management/grants"

    def get_route_url_with_id(self, instance):
        return f"/{instance.project.id}/members/{instance.member.id}/data-management/grants/{instance.id}"

    def get_route_url_history(self, instance):
        return f"/{instance.project.id}/members/{instance.member.id}/data-management/grants/{instance.id}/history/events"

    def get_route_url_history_with_id(self, instance, event):
        return f"/{instance.project.id}/members/{instance.member.id}/data-management/grants/{instance.id}/history/events/{event.pgh_id}"

    def get_route_url_history_revert(self, instance, event):
        return f"/{instance.project.id}/members/{instance.member.id}/data-management/grants/{instance.id}/history/events/{event.pgh_id}/reversion"

    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_delete(self, scenario, config):
        for i in range(self.SUBTESTS):
            instance = self.INSTANCE[i]
            config = {**config, "expected_responses": (201, 403, 401, 301)}
            # Call the API endpoint
            response = self.call_api_endpoint(
                "DELETE", self.get_route_url_with_id(instance), **config
            )
            with self.subTest(i=i):
                # Assert response content
                if scenario == "HTTPS Authenticated":
                    self.assertEqual(response.status_code, 201)
                    instance = self.MODEL[i].objects.filter(id=instance.id).first()
                    self.assertIsNotNone(instance)
                    self.assertTrue(instance.revoked)
