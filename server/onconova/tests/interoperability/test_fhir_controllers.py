from django.test import TestCase
from parameterized import parameterized
from unittest.mock import patch
from onconova.oncology import models
from onconova.interoperability.fhir import schemas
from onconova.tests import factories
from onconova.tests.common import (
    GET_HTTP_SCENARIOS,
    HTTP_SCENARIOS,
    ApiControllerTestMixin,
)
from typing import List, Type
from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Coding
from factory.django import DjangoModelFactory
from ninja import Schema
import pghistory
from onconova.core.models import BaseModel


class FhirCrudApiControllerTestCase(ApiControllerTestMixin, TestCase):

    # Public interface
    FACTORY: type[DjangoModelFactory] | List[type[DjangoModelFactory]]
    factories: List[type[DjangoModelFactory]]
    MODEL: Type[BaseModel] | List[Type[BaseModel]]
    SCHEMA: Type[Schema] | List[Type[Schema]]

    # Internal state
    models: List[Type[BaseModel]]
    schemas: List[Type[Schema]]
    create_schemas: List[Type[Schema]]

    __test__ = False  # Prevent pytest from collecting this base class as a test

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Ensure subclasses are collected as tests
        cls.__test__ = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Ensure class settings are iterable
        cls.factories = (
            [cls.FACTORY] if not isinstance(cls.FACTORY, list) else cls.FACTORY
        )
        cls.subtests = len(cls.factories)
        cls.models = (
            [cls.MODEL] * cls.subtests if not isinstance(cls.MODEL, list) else cls.MODEL
        )
        cls.schemas = (
            [cls.SCHEMA] * cls.subtests
            if not isinstance(cls.SCHEMA, list)
            else cls.SCHEMA
        )
        cls.create_schemas = (
            [cls.SCHEMA] * cls.subtests
            if not isinstance(cls.SCHEMA, list)
            else cls.SCHEMA
        )
        cls.instances = []
        cls.create_payloads = []
        cls.update_payloads = []
        for factory, schema in zip(cls.factories, cls.create_schemas):
            with pghistory.context(username=cls.user.username):
                instance1, instance2 = factory.create_batch(2)
                if hasattr(cls, "post_factory_hook"):
                    instance1, instance2 = cls.post_factory_hook(instance1, instance2)
                cls.instances.append(instance1)
                cls.create_payloads.append(
                    schema.model_validate(instance1).model_dump(mode="json")
                )
                cls.update_payloads.append(
                    schema.model_validate(instance2).model_dump(mode="json")
                )
                instance2.delete()

    @parameterized.expand(
        GET_HTTP_SCENARIOS,
        name_func=lambda testcase_func, _, param: f'{testcase_func.__name__}_{param[0][0].lower().replace(" ","_")}_{"authorized" if param[0][1]["access_level"]>1 else "unauthorized"}',
    )
    def test_read_operation(self, scenario, config, *args):
        for i, (instance, schema, model) in enumerate(
            zip(self.instances, self.schemas, self.models)
        ):
            # Call the API endpoint
            response = self.call_api_endpoint(
                "GET",
                self.get_route_url_with_id(instance),
                anonymized=False,
                **config,
            )
            # Assert response content
            if scenario == "HTTPS Authenticated":
                self.assertEqual(response.status_code, 200)
                expected = schema.model_validate(instance).model_dump()
                for c in expected.get("contained", []):
                    c.pop("meta", None)
                result = response.json()
                for c in result.get("contained", []):
                    c.pop("meta", None)
                self.assertEqual(
                    result,
                    expected,
                    f"Response FHIR data does not match expected for {model.__name__}",
                )

    @parameterized.expand(
        HTTP_SCENARIOS,
        name_func=lambda testcase_func, _, param: f'{testcase_func.__name__}_{param[0][0].lower().replace(" ","_")}_{"authorized" if param[0][1]["access_level"]>1 else "unauthorized"}',
    )
    def test_delete_operation(self, scenario, config):
        for i, (instance, model) in enumerate(zip(self.instances, self.models)):
            # Call the API endpoint
            response = self.call_api_endpoint(
                "DELETE", self.get_route_url_with_id(instance), **config
            )
            # Assert response content
            if scenario == "HTTPS Authenticated":
                self.assertEqual(response.status_code, 204)
                self.assertFalse(model.objects.filter(id=instance.id).exists())
                # Assert audit trail
                self.assertTrue(
                    pghistory.models.Events.objects.filter(  # type: ignore
                        pgh_obj_id=instance.id, pgh_label="delete"
                    ).exists(),
                    "Event not properly registered",
                )

    @parameterized.expand(
        HTTP_SCENARIOS,
        name_func=lambda testcase_func, _, param: f'{testcase_func.__name__}_{param[0][0].lower().replace(" ","_")}_{"authorized" if param[0][1]["access_level"]>1 else "unauthorized"}',
    )
    def test_create_operation(self, scenario, config, *args):
        for i, (instance, payload, model) in enumerate(
            zip(self.instances, self.create_payloads, self.models)
        ):
            instance.delete()
            # Call the API endpoint.
            response = self.call_api_endpoint(
                "POST", self.get_route_url(instance), data=payload, **config
            )
            # Assert response content
            if scenario == "HTTPS Authenticated":
                created_id = response.json()["id"]
                created_instance = model.objects.filter(id=created_id).first()
                assert created_instance is not None, "Resource has not been created"
                # Assert audit trail
                self.assertEqual(
                    self.user.username,
                    created_instance.created_by,
                    "Unexpected creator user.",
                )
                self.assertTrue(
                    created_instance.events.filter(pgh_label="create").exists(),  # type: ignore
                    "Event not properly registered",
                )

    @parameterized.expand(
        HTTP_SCENARIOS,
        name_func=lambda testcase_func, _, param: f'{testcase_func.__name__}_{param[0][0].lower().replace(" ","_")}_{"authorized" if param[0][1]["access_level"]>1 else "unauthorized"}',
    )
    def test_update_operation(self, scenario, config, *args):
        for i, (instance, payload, model) in enumerate(
            zip(self.instances, self.update_payloads, self.models)
        ):
            payload["id"] = str(instance.id)
            # Call the API endpoint
            response = self.call_api_endpoint(
                "PUT", self.get_route_url_with_id(instance), data=payload, **config
            )
            # Assert response content
            if scenario == "HTTPS Authenticated":
                updated_id = response.json()["id"]
                self.assertEqual(response.status_code, 200)
                updated_instance = model.objects.filter(id=updated_id).first()
                assert (
                    updated_instance is not None
                ), "The updated instance does not exist"
                self.assertNotEqual(
                    [
                        getattr(instance, field.name)
                        for field in model._meta.concrete_fields
                    ],
                    [
                        getattr(updated_instance, field.name)
                        for field in model._meta.concrete_fields
                    ],
                )
                # Assert audit trail
                if updated_instance.updated_by:
                    self.assertIn(
                        self.user.username,
                        updated_instance.updated_by,  # type: ignore
                        "The updating user is not registered",
                    )
                self.assertTrue(
                    pghistory.models.Events.objects.filter(  # type: ignore
                        pgh_obj_id=instance.id, pgh_label="update"
                    ).exists(),
                    "Event not properly registered",
                )


class TestPatientsController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Patient"
    FACTORY = factories.PatientCaseFactory
    MODEL = models.PatientCase
    SCHEMA = schemas.CancerPatientProfile

    def setUp(self):
        super().setUp()
        self.patcher = patch(
            "onconova.interoperability.fhir.schemas.cancer_patient.CancerPatientProfile._get_birthsex_codesystem",
            autospec=True,
            return_value="http://test.org/codesystem/birthsex",
        )
        self.mock_function = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.patcher = patch(
            "onconova.interoperability.fhir.schemas.cancer_patient.CancerPatientProfile._get_gender_codesystem",
            autospec=True,
            return_value="http://test.org/codesystem/administrativegender",
        )
        self.mock_function = self.patcher.start()
        self.addCleanup(self.patcher.stop)


class TestPrimaryNeoplasticEntityConditionController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Condition"
    FACTORY = factories.PrimaryNeoplasticEntityFactory
    MODEL = models.NeoplasticEntity
    SCHEMA = schemas.PrimaryCancerConditionProfile


class TestMetastaticNeoplasticEntityConditionController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Condition"
    FACTORY = factories.MetastaticNeoplasticEntityFactory
    MODEL = models.NeoplasticEntity
    SCHEMA = schemas.SecondaryCancerConditionProfile


class TestTumorMarkerObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.TumorMarkerTestFactory
    MODEL = models.TumorMarker
    SCHEMA = schemas.TumorMarkerProfile

    @classmethod
    def setUpTestData(cls):
        cls.patcher = patch(
            "onconova.interoperability.fhir.schemas.tumor_marker.TumorMarkerProfile.map_to_fhir",
            return_value=Coding(
                code="9811-1",
                system="http://loinc.org",
                display="Chromogranin A [Mass/volume] in Serum or Plasma",
            ),
        )
        cls.mock_to_fhir = cls.patcher.start()
        super().setUpTestData()

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
        super().tearDownClass()


class TestRiskAssessmentObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.RiskAssessmentFactory
    MODEL = models.RiskAssessment
    SCHEMA = schemas.CancerRiskAssessmentProfile


class TestGenomicVariantObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.GenomicVariantFactory
    MODEL = models.GenomicVariant
    SCHEMA = schemas.GenomicVariantProfile


class TestTumorMutationalBurdenObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.TumorMutationalBurdenFactory
    MODEL = models.TumorMutationalBurden
    SCHEMA = schemas.TumorMutationalBurdenProfile


class TestMicrosatelliteInstabilityObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.MicrosatelliteInstabilityFactory
    MODEL = models.MicrosatelliteInstability
    SCHEMA = schemas.MicrosatelliteInstabilityProfile


class TestLossOfHeterozygosityObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.LossOfHeterozygosityFactory
    MODEL = models.LossOfHeterozygosity
    SCHEMA = schemas.LossOfHeterozygosityProfile


class TestHomologousRecombinationDeficiencyObservationController(
    FhirCrudApiControllerTestCase
):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.HomologousRecombinationDeficiencyFactory
    MODEL = models.HomologousRecombinationDeficiency
    SCHEMA = schemas.HomologousRecombinationDeficiencyProfile


class TestTumorNeoantigenBurdenObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.TumorNeoantigenBurdenFactory
    MODEL = models.TumorNeoantigenBurden
    SCHEMA = schemas.TumorNeoantigenBurdenProfile


class TestAneuploidScoreObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.AneuploidScoreFactory
    MODEL = models.AneuploidScore
    SCHEMA = schemas.AneuploidScoreProfile


class TestComorbiditiesAssessmentObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.ComorbiditiesAssessmentFactory
    MODEL = models.ComorbiditiesAssessment
    SCHEMA = schemas.ComorbiditiesProfile


class TestLifestyleObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.LifestyleFactory
    MODEL = models.Lifestyle
    SCHEMA = schemas.LifestyleProfile


class TestECOGPerformanceStatusObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.ECOGPerformanceStatusFactory
    MODEL = models.PerformanceStatus
    SCHEMA = schemas.ECOGPerformanceStatusProfile


class TestKarnofskyPerformanceStatusObservationController(
    FhirCrudApiControllerTestCase
):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.KarnofskyPerformanceStatusFactory
    MODEL = models.PerformanceStatus
    SCHEMA = schemas.KarnofskyPerformanceStatusProfile


class TestTreatmentResponseObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.TreatmentResponseFactory
    MODEL = models.TreatmentResponse
    SCHEMA = schemas.ImagingDiseaseStatusProfile


class TestFIGOStagingObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.FIGOStagingFactory
    MODEL = models.FIGOStaging
    SCHEMA = schemas.CancerStageProfile


class TestRaiStagingObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.RaiStagingFactory
    MODEL = models.RaiStaging
    SCHEMA = schemas.CancerStageProfile


class TestBreslowDepthObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.BreslowDepthFactory
    MODEL = models.BreslowDepth
    SCHEMA = schemas.CancerStageProfile


class TestBinetStagingObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.BinetStagingFactory
    MODEL = models.BinetStaging
    SCHEMA = schemas.CancerStageProfile


class TestClarkStagingObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.ClarkStagingFactory
    MODEL = models.ClarkStaging
    SCHEMA = schemas.CancerStageProfile


class TestISSStagingObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.ISSStagingFactory
    MODEL = models.ISSStaging
    SCHEMA = schemas.CancerStageProfile


class TestRISSStagingObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.RISSStagingFactory
    MODEL = models.RISSStaging
    SCHEMA = schemas.CancerStageProfile


class TestINSSStagingObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.INSSStagingFactory
    MODEL = models.INSSStage
    SCHEMA = schemas.CancerStageProfile


class TestINRGSSStagingObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.INRGSSStagingFactory
    MODEL = models.INRGSSStage
    SCHEMA = schemas.CancerStageProfile


class TestGleasonGradeObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.GleasonGradeFactory
    MODEL = models.GleasonGrade
    SCHEMA = schemas.CancerStageProfile


class TestRhabdomyosarcomaClinicalGroupObservationController(
    FhirCrudApiControllerTestCase
):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.RhabdomyosarcomaClinicalGroupFactory
    MODEL = models.RhabdomyosarcomaClinicalGroup
    SCHEMA = schemas.CancerStageProfile


class TestWilmsStageObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.WilmsStageFactory
    MODEL = models.WilmsStage
    SCHEMA = schemas.CancerStageProfile


class TestTNMStagingObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.TNMStagingFactory
    MODEL = models.TNMStaging
    SCHEMA = schemas.TNMStageGroupProfile


class TestLymphomaStagingObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.LymphomaStagingFactory
    MODEL = models.LymphomaStaging
    SCHEMA = schemas.LymphomaStageProfile


class TestVitalsObservationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = factories.VitalsFactory
    MODEL = models.Vitals
    SCHEMA = schemas.VitalsPanelProfile


class TestSurgeryProceduresController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Procedure"
    FACTORY = factories.SurgeryFactory
    MODEL = models.Surgery
    SCHEMA = schemas.SurgicalProcedureProfile


class TestRadiotherapyProceduresController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Procedure"
    FACTORY = factories.RadiotherapyFactory
    MODEL = models.Radiotherapy
    SCHEMA = schemas.RadiotherapyCourseSummaryProfile


class TestUnspecifiedTumorBoardProceduresController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Procedure"
    FACTORY = factories.TumorBoardFactory
    MODEL = models.UnspecifiedTumorBoard
    SCHEMA = schemas.TumorBoardReviewProfile


class TestMolecularTumorBoardProceduresController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Procedure"
    FACTORY = factories.MolecularTumorBoardFactory
    MODEL = models.MolecularTumorBoard
    SCHEMA = schemas.MolecularTumorBoardReviewProfile


class TestAdverseEventsController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/AdverseEvent"
    FACTORY = factories.AdverseEventFactory
    MODEL = models.AdverseEvent
    SCHEMA = schemas.AdverseEventProfile


class TestFamilyMemberHistoryController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/FamilyMemberHistory"
    FACTORY = factories.FamilyHistoryFactory
    MODEL = models.FamilyHistory
    SCHEMA = schemas.CancerFamilyMemberHistoryProfile


class TestMedicationAdministrationController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/MedicationAdministration"
    FACTORY = factories.SystemicTherapyFactory
    MODEL = models.SystemicTherapy
    SCHEMA = schemas.MedicationAdministrationProfile


class TestEpisodeOfCareController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/EpisodeOfCare"
    FACTORY = factories.TherapyLineFactory
    MODEL = models.TherapyLine
    SCHEMA = schemas.TherapyLineProfile
