from collections import Counter
from datetime import datetime

from django.test import TestCase
from parameterized import parameterized

from onconova.core.utils import average, percentile, std
from onconova.research import models, schemas
from onconova.tests import factories
from onconova.tests.common import (
    GET_HTTP_SCENARIOS,
    HTTP_SCENARIOS,
    ApiControllerTestMixin,
    CrudApiControllerTestCase,
)


class TestCohortController(CrudApiControllerTestCase):
    controller_path = "/api/v1/cohorts"
    FACTORY = factories.CohortFactory
    MODEL = models.Cohort
    SCHEMA = schemas.CohortSchema
    CREATE_SCHEMA = schemas.CohortCreateSchema

    @parameterized.expand(
        [
            ("member", True, 1, 201),
            ("non-member member", False, 1, 403),
            ("member leader", True, 2, 201),
            ("non-member leader", False, 2, 403),
            ("member platform manager ", True, 3, 201),
            ("non-member platform manager", False, 3, 201),
        ]
    )
    def test_project_cohort_create_permissions(
        self, scenario, is_member, access_level, expected_response
    ):
        project = factories.ProjectFactory.create()
        cohort = factories.CohortFactory(project=project)
        if is_member:
            if access_level == 1:
                project.members.add(self.user)
            elif access_level == 2:
                project.leader = self.user
            project.save()
        self.call_api_endpoint(
            "POST",
            f"",
            data=schemas.CohortCreateSchema.model_validate(cohort).model_dump(),
            authenticated=True,
            expected_responses=(expected_response,),
            use_https=True,
            access_level=access_level,
        )

    @parameterized.expand(
        [
            ("member", True, 1, 200),
            ("non-member member", False, 1, 403),
            ("member leader", True, 2, 200),
            ("non-member leader", False, 2, 403),
            ("member platform manager ", True, 3, 200),
            ("non-member platform manager", False, 3, 200),
        ]
    )
    def test_project_cohort_update_permissions(
        self, scenario, is_member, access_level, expected_response
    ):
        project = factories.ProjectFactory.create()
        cohort = factories.CohortFactory(project=project)
        if is_member:
            if access_level == 1:
                project.members.add(self.user)
            elif access_level == 2:
                project.leader = self.user
            project.save()
        self.call_api_endpoint(
            "PUT",
            f"/{cohort.id}",
            data=schemas.CohortCreateSchema.model_validate(cohort).model_dump(),
            authenticated=True,
            expected_responses=(expected_response,),
            use_https=True,
            access_level=access_level,
        )


class TestCohortTraitsController(ApiControllerTestMixin, TestCase):
    controller_path = "/api/v1/cohorts"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.trait = "age"
        cls.cohort = factories.CohortFactory.create()
        cls.cohort.cases.set(
            [
                factories.PatientCaseFactory.create(
                    consent_status="valid",
                    vital_status="alive",
                    date_of_birth=datetime(2000 + i, 1, 1).date(),
                    date_of_death=None,
                )
                for i in range(10)
            ]
        )

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_get_cohort_traits_statistics(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint("GET", f"/{self.cohort.id}/traits", **config)
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)

            # Assert median age in response
            values = [getattr(case, "age") for case in self.cohort.valid_cases.all()]
            interp_diff = 0.5
            expected = schemas.cohort.CohortTraitMedian(
                median=percentile(values, 50) - interp_diff,
                interQuartalRange=(
                    percentile(values, 25) - interp_diff,
                    percentile(values, 75) - interp_diff,
                ),
            ).model_dump()
            result = schemas.cohort.CohortTraits.model_validate(
                response.json()
            ).age.model_dump()
            self.assertDictEqual(result, expected)

            # Assert gender counts in response
            counter = Counter(
                [case.gender.display for case in self.cohort.valid_cases.all()]
            )
            expected = [
                schemas.cohort.CohortTraitCounts(
                    category=category,
                    counts=count,
                    percentage=round(count / self.cohort.cases.count() * 100, 4),
                ).model_dump()
                for category, count in counter.items()
            ]
            result = [
                count.model_dump()
                for count in schemas.cohort.CohortTraits.model_validate(
                    response.json()
                ).genders
            ]
            self.assertEqual(result, expected)


class TestDatasetController(CrudApiControllerTestCase):
    controller_path = "/api/v1/datasets"
    FACTORY = factories.DatasetFactory
    MODEL = models.Dataset
    SCHEMA = schemas.Dataset
    CREATE_SCHEMA = schemas.DatasetCreate

    @parameterized.expand(
        [
            ("member", True, 1, 201),
            ("non-member member", False, 1, 403),
            ("member leader", True, 2, 201),
            ("non-member leader", False, 2, 403),
            ("member platform manager ", True, 3, 201),
            ("non-member platform manager", False, 3, 201),
        ]
    )
    def test_project_dataset_create_permissions(
        self, scenario, is_member, access_level, expected_response
    ):
        project = factories.ProjectFactory.create()
        dataset = factories.DatasetFactory(project=project)
        if is_member:
            if access_level == 1:
                project.members.add(self.user)
            elif access_level == 2:
                project.leader = self.user
            project.save()
        self.call_api_endpoint(
            "POST",
            f"",
            data=schemas.DatasetCreate.model_validate(dataset).model_dump(),
            authenticated=True,
            expected_responses=(expected_response,),
            use_https=True,
            access_level=access_level,
        )

    @parameterized.expand(
        [
            ("member", True, 1, 200),
            ("non-member member", False, 1, 403),
            ("member leader", True, 2, 200),
            ("non-member leader", False, 2, 403),
            ("member platform manager ", True, 3, 200),
            ("non-member platform manager", False, 3, 200),
        ]
    )
    def test_project_dataset_update_permissions(
        self, scenario, is_member, access_level, expected_response
    ):
        project = factories.ProjectFactory.create()
        dataset = factories.DatasetFactory(project=project)
        if is_member:
            if access_level == 1:
                project.members.add(self.user)
            elif access_level == 2:
                project.leader = self.user
            project.save()
        self.call_api_endpoint(
            "PUT",
            f"/{dataset.id}",
            data=schemas.DatasetCreate.model_validate(dataset).model_dump(),
            authenticated=True,
            expected_responses=(expected_response,),
            use_https=True,
            access_level=access_level,
        )


class TestProjectController(CrudApiControllerTestCase):
    controller_path = "/api/v1/projects"
    FACTORY = factories.ProjectFactory
    MODEL = models.Project
    SCHEMA = schemas.ProjectSchema
    CREATE_SCHEMA = schemas.ProjectCreateSchema

    @parameterized.expand(
        [
            ("member", True, 1, 403),
            ("non-member member", False, 1, 403),
            ("member leader", True, 2, 200),
            ("non-member leader", False, 2, 403),
            ("member platform manager ", True, 3, 200),
            ("non-member platform manager", False, 3, 200),
        ]
    )
    def test_project_management_permissions(
        self, scenario, is_member, access_level, expected_response
    ):
        project = factories.ProjectFactory.create()
        if is_member:
            if access_level == 1:
                project.members.add(self.user)
            elif access_level == 2:
                project.leader = self.user
            project.save()
        self.call_api_endpoint(
            "PUT",
            f"/{project.id}",
            data=schemas.ProjectCreateSchema.model_validate(project).model_dump(),
            authenticated=True,
            expected_responses=(expected_response,),
            use_https=True,
            access_level=access_level,
        )


class TestProjectDataManagerController(CrudApiControllerTestCase):
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

    @parameterized.expand(HTTP_SCENARIOS)
    def test_delete(self, scenario, config):
        for i in range(self.subtests):
            instance = self.instances[i]
            config = {**config, "expected_responses": (201, 403, 401, 301)}
            # Call the API endpoint
            response = self.call_api_endpoint(
                "DELETE", self.get_route_url_with_id(instance), **config
            )
            with self.subTest(i=i):
                # Assert response content
                if scenario == "HTTPS Authenticated":
                    self.assertEqual(response.status_code, 201)
                    instance = self.models[i].objects.filter(id=instance.id).first()
                    self.assertIsNotNone(instance)
                    self.assertTrue(instance.revoked)  # type: ignore

    @parameterized.expand(
        [
            ("member", True, 1, 403),
            ("non-member member", False, 1, 403),
            ("member leader", True, 2, 201),
            ("non-member leader", False, 2, 403),
            ("member platform manager ", True, 3, 201),
            ("non-member platform manager", False, 3, 201),
        ]
    )
    def test_project_data_management_grant_permissions(
        self, scenario, is_member, access_level, expected_response
    ):
        project = factories.ProjectFactory.create()
        grant = factories.ProjectDataManagerGrantFactory(
            project=project, member=self.user
        )
        if is_member:
            if access_level == 1:
                project.members.add(self.user)
            elif access_level == 2:
                project.leader = self.user
            project.save()
        self.call_api_endpoint(
            "POST",
            f"/{project.id}/members/{self.user.id}/data-management/grants",
            data=schemas.ProjectDataManagerGrantCreateSchema.model_validate(
                grant
            ).model_dump(),
            authenticated=True,
            expected_responses=(expected_response,),
            use_https=True,
            access_level=access_level,
        )

    @parameterized.expand(
        [
            ("member", True, 1, 403),
            ("non-member member", False, 1, 403),
            ("member leader", True, 2, 201),
            ("non-member leader", False, 2, 403),
            ("member platform manager ", True, 3, 201),
            ("non-member platform manager", False, 3, 201),
        ]
    )
    def test_project_data_management_revoke_permissions(
        self, scenario, is_member, access_level, expected_response
    ):
        project = factories.ProjectFactory.create()
        grant = factories.ProjectDataManagerGrantFactory(
            project=project, member=self.user
        )
        if is_member:
            if access_level == 1:
                project.members.add(self.user)
            elif access_level == 2:
                project.leader = self.user
            project.save()
        self.call_api_endpoint(
            "DELETE",
            f"/{project.id}/members/{self.user.id}/data-management/grants/{grant.id}",
            authenticated=True,
            expected_responses=(expected_response,),
            use_https=True,
            access_level=access_level,
        )
