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
from fhircraft.fhir.resources.datatypes.R4.complex import Coding
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
                cls.instances.append(instance1)
                cls.create_payloads.append(
                    schema.model_validate(instance1).model_dump(mode="json")
                )
                cls.update_payloads.append(
                    schema.model_validate(instance2).model_dump(mode="json")
                )
                instance2.delete()

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_read_operation(self, scenario, config, *args):
        for i, (instance, schema, model) in enumerate(
            zip(self.instances, self.schemas, self.models)
        ):
            with self.subTest(i=i):
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
                    result = schema.model_validate(response.json()).model_dump()
                    self.assertEqual(
                        result,
                        expected,
                        f"Response FHIR data does not match expected for {model.__name__}",
                    )

    @parameterized.expand(HTTP_SCENARIOS)
    def test_delete_operation(self, scenario, config):
        for i, (instance, schema, model) in enumerate(
            zip(self.instances, self.schemas, self.models)
        ):
            with self.subTest(i=i):
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

    @parameterized.expand(HTTP_SCENARIOS)
    def test_create_operation(self, scenario, config, *args):
        for i, (instance, payload, model) in enumerate(
            zip(self.instances, self.create_payloads, self.models)
        ):
            with self.subTest(i=i):
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

    @parameterized.expand(HTTP_SCENARIOS)
    def test_update_operation(self, scenario, config, *args):
        for i, (instance, payload, model) in enumerate(
            zip(self.instances, self.update_payloads, self.models)
        ):
            with self.subTest(i=i):
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


class TestConditionsController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Condition"
    FACTORY = [
        factories.PrimaryNeoplasticEntityFactory,
        factories.MetastaticNeoplasticEntityFactory,
    ]
    MODEL = [models.NeoplasticEntity, models.NeoplasticEntity]
    SCHEMA = [
        schemas.PrimaryCancerConditionProfile,
        schemas.SecondaryCancerConditionProfile,
    ]


class TestObservationsController(FhirCrudApiControllerTestCase):
    controller_path = "/api/fhir/Observation"
    FACTORY = [
        factories.TumorMarkerTestFactory,
        factories.RiskAssessmentFactory,
        factories.GenomicVariantFactory,
        factories.TumorMutationalBurdenFactory,
        factories.MicrosatelliteInstabilityFactory,
        factories.LossOfHeterozygosityFactory,
        factories.HomologousRecombinationDeficiencyFactory,
        factories.TumorNeoantigenBurdenFactory,
        factories.AneuploidScoreFactory,
        factories.ComorbiditiesAssessmentFactory,
        factories.LifestyleFactory,
        factories.ECOGPerformanceStatusFactory,
        factories.KarnofskyPerformanceStatusFactory,
        factories.TreatmentResponseFactory,
        factories.FIGOStagingFactory,
        factories.RaiStagingFactory,
        factories.BreslowDepthFactory,
        factories.BinetStagingFactory,
        factories.ClarkStagingFactory,
        factories.ISSStagingFactory,
        factories.RISSStagingFactory,
        factories.INSSStagingFactory,
        factories.INRGSSStagingFactory,
        factories.GleasonGradeFactory,
        factories.RhabdomyosarcomaClinicalGroupFactory,
        factories.WilmsStageFactory,
    ]
    MODEL = [
        models.TumorMarker,
        models.RiskAssessment,
        models.GenomicVariant,
        models.TumorMutationalBurden,
        models.MicrosatelliteInstability,
        models.LossOfHeterozygosity,
        models.HomologousRecombinationDeficiency,
        models.TumorNeoantigenBurden,
        models.AneuploidScore,
        models.ComorbiditiesAssessment,
        models.Lifestyle,
        models.PerformanceStatus,
        models.PerformanceStatus,
        models.TreatmentResponse,
        models.FIGOStaging,
        models.RaiStaging,            
        models.BreslowDepth,            
        models.BinetStaging,            
        models.ClarkStaging,            
        models.ISSStaging,            
        models.RISSStaging,            
        models.INSSStage,            
        models.INRGSSStage,            
        models.GleasonGrade,            
        models.RhabdomyosarcomaClinicalGroup,            
        models.WilmsStage,    
    ]
    SCHEMA = [
        schemas.TumorMarkerProfile,
        schemas.CancerRiskAssessmentProfile,
        schemas.GenomicVariantProfile,
        schemas.TumorMutationalBurdenProfile,
        schemas.MicrosatelliteInstabilityProfile,
        schemas.LossOfHeterozygosityProfile,
        schemas.HomologousRecombinationDeficiencyProfile,
        schemas.TumorNeoantigenBurdenProfile,
        schemas.AneuploidScoreProfile,
        schemas.ComorbiditiesProfile,
        schemas.LifestyleProfile,
        schemas.ECOGPerformanceStatusProfile,
        schemas.KarnofskyPerformanceStatusProfile,
        schemas.ImagingDiseaseStatusProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
        schemas.CancerStageProfile,
    ]

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

