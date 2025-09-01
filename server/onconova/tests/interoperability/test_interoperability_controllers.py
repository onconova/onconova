import re

import pghistory
from django.conf import settings
from django.test import TestCase
from parameterized import parameterized

from onconova.core.history.schemas import HistoryEvent
from onconova.interoperability.schemas import PatientCaseBundle, UserExportSchema
from onconova.oncology.models import PatientCase
from onconova.tests import common, factories
from onconova.tests.common import GET_HTTP_SCENARIOS, ApiControllerTestMixin


class TestInteroperabilityController(ApiControllerTestMixin, TestCase):
    controller_path = "/api/v1/interoperability"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        with pghistory.context(username=cls.user.username):
            cls.case = factories.PatientCaseFactory.create()
            cls.entity = factories.PrimaryNeoplasticEntityFactory.create(case=cls.case)
            cls.systemic_therapy = factories.SystemicTherapyFactory.create(
                case=cls.case, therapy_line=None, targeted_entities=[cls.entity]
            )
            cls.case.save()
            cls.case.refresh_from_db()
            cls.entity.save()
            cls.entity.refresh_from_db()
            cohort = factories.CohortFactory()
            cohort.cases.add(cls.case)
            cls.bundle = PatientCaseBundle.model_validate(cls.case)
            cls.bundle.history = [
                HistoryEvent.model_validate(event)
                for event in cls.bundle.resolve_history(cls.case)
            ]
            cls.bundle.contributorsDetails = [
                UserExportSchema.model_validate(user)
                for user in cls.bundle.resolve_contributorsDetails(cls.case)
            ]
            cls.bundle = cls.bundle.anonymize_users(cls.bundle)
            cls.payload = cls.bundle.model_dump(mode="json")

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_export_resource(self, scenario, config):
        response = self.call_api_endpoint(
            "GET", f"/resources/{self.entity.id}", **config
        )
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            export = response.json()
            self.assertEqual(self.user.username, export["exportedBy"])
            self.assertEqual(settings.VERSION, export["exportVersion"])
            self.assertTrue(re.findall(r"([a-fA-F\d]{32})", export["checksum"]))
            self.assertTrue(
                self.entity.events.filter(pgh_label="export").exists(),
                "Event not properly registered",
            )

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_resolve_resource_id(self, scenario, config):
        response = self.call_api_endpoint(
            "GET", f"/resources/{self.entity.id}/description", **config
        )
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.entity.description, response.json())

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_export_bundle(self, scenario, config):
        response = self.call_api_endpoint("GET", f"/bundles/{self.case.id}", **config)
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            entry = response.json()
            self.assertEqual(
                self.case.neoplastic_entities.all().count(),
                len(entry["neoplasticEntities"]),
            )
            self.assertEqual(
                self.case.systemic_therapies.all().count(),
                len(entry["systemicTherapies"]),
            )
            self.assertEqual(self.case.stagings.all().count(), len(entry["stagings"]))
            self.assertTrue(
                self.case.events.filter(pgh_label="export").exists(),
                "Event not properly registered",
            )

    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_import_bundle(self, scenario, config):
        self.case.delete()
        response = self.call_api_endpoint(
            "POST", "/bundles", data=self.payload, **config
        )
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 201)
            imported_case = PatientCase.objects.get(
                pseudoidentifier=self.bundle.pseudoidentifier
            )
            self.assertEqual(
                self.case.clinical_identifier, imported_case.clinical_identifier
            )
            self.assertTrue(
                imported_case.events.filter(pgh_label="import").exists(),
                "Import event not properly registered",
            )
            self.assertTrue(
                imported_case.events.filter(pgh_label="create").exists(),
                "Create event not properly registered",
            )

    def test_import_conflicting_bundle_unresolved(self):
        response = self.call_api_endpoint(
            "POST",
            "/bundles",
            data=self.payload,
            expected_responses=[422],
            authenticated=True,
            use_https=True,
            access_level=4,
        )
        self.assertEqual(response.status_code, 422)

    def test_import_conflicting_bundle_overwrite(self):
        response = self.call_api_endpoint(
            "POST",
            "/bundles?conflict=overwrite",
            data=self.payload,
            expected_responses=[201],
            authenticated=True,
            use_https=True,
            access_level=4,
        )
        self.assertEqual(response.status_code, 201)
        new_case = PatientCase.objects.get(
            pseudoidentifier=self.bundle.pseudoidentifier
        )
        self.assertEqual(self.case.clinical_identifier, new_case.clinical_identifier)
        self.assertEqual(self.case.id, new_case.id)
        imported_case = PatientCase.objects.filter(id=self.case.id).first()
        self.assertIsNotNone(imported_case)
        self.assertEqual(imported_case.neoplastic_entities.count(), 1)
        self.assertEqual(imported_case.systemic_therapies.count(), 1)

    def test_import_conflicting_bundle_reassign(self):
        self.payload["clinicalIdentifier"] = "123456789"
        response = self.call_api_endpoint(
            "POST",
            "/bundles?conflict=reassign",
            data=self.payload,
            expected_responses=[201],
            authenticated=True,
            use_https=True,
            access_level=4,
        )
        self.assertEqual(response.status_code, 201)
        new_case = PatientCase.objects.get(clinical_identifier="123456789")
        self.assertNotEqual(self.case.clinical_identifier, new_case.clinical_identifier)
        self.assertNotEqual(self.case.id, new_case.id)
        imported_case = PatientCase.objects.filter(id=self.case.id).first()
        self.assertIsNotNone(imported_case)
        self.assertTrue(imported_case, "Event not properly registered")

    def test_import_conflicting_reassign_but_conflicting_clinical_identifier(self):
        response = self.call_api_endpoint(
            "POST",
            "/bundles?conflict=reassign",
            data=self.payload,
            expected_responses=[422],
            authenticated=True,
            use_https=True,
            access_level=4,
        )
        self.assertEqual(response.status_code, 422)
