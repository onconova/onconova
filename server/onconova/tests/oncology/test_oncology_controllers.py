from django.test import TestCase
from parameterized import parameterized

from onconova.oncology import models, schemas
from onconova.tests import common, factories
from onconova.tests.common import CrudApiControllerTestCase


class TestPatientCaseController(CrudApiControllerTestCase):
    controller_path = "/api/v1/patient-cases"
    FACTORY = factories.PatientCaseFactory
    MODEL = models.PatientCase
    SCHEMA = schemas.PatientCaseSchema
    CREATE_SCHEMA = schemas.PatientCaseCreateSchema


class TestNeoplasticEntityController(CrudApiControllerTestCase):
    controller_path = "/api/v1/neoplastic-entities"
    FACTORY = factories.PrimaryNeoplasticEntityFactory
    MODEL = models.NeoplasticEntity
    SCHEMA = schemas.NeoplasticEntitySchema
    CREATE_SCHEMA = schemas.NeoplasticEntityCreateSchema


class TestStagingController(CrudApiControllerTestCase):
    controller_path = "/api/v1/stagings"
    FACTORY = [
        factories.TNMStagingFactory,
        factories.FIGOStagingFactory,
    ]
    MODEL = [
        models.TNMStaging,
        models.FIGOStaging,
    ]
    SCHEMA = [
        schemas.TNMStagingSchema,
        schemas.FIGOStagingSchema,
    ]
    CREATE_SCHEMA = [schemas.TNMStagingCreateSchema, schemas.FIGOStagingCreateSchema]


class TestTumorMarkerController(CrudApiControllerTestCase):
    controller_path = "/api/v1/tumor-markers"
    FACTORY = factories.TumorMarkerTestFactory
    MODEL = models.TumorMarker
    SCHEMA = schemas.TumorMarkerSchema
    CREATE_SCHEMA = schemas.TumorMarkerCreateSchema


class TestRiskAssessmentController(CrudApiControllerTestCase):
    controller_path = "/api/v1/risk-assessments"
    FACTORY = factories.RiskAssessmentFactory
    MODEL = models.RiskAssessment
    SCHEMA = schemas.RiskAssessmentSchema
    CREATE_SCHEMA = schemas.RiskAssessmentCreateSchema


class TestSystemicTherapyController(CrudApiControllerTestCase):
    controller_path = "/api/v1/systemic-therapies"
    FACTORY = factories.SystemicTherapyFactory
    MODEL = models.SystemicTherapy
    SCHEMA = schemas.SystemicTherapySchema
    CREATE_SCHEMA = schemas.SystemicTherapyCreateSchema


class TestSystemicTherapyMedicationController(CrudApiControllerTestCase):
    controller_path = "/api/v1/systemic-therapies"
    FACTORY = factories.SystemicTherapyMedicationFactory
    MODEL = models.SystemicTherapyMedication
    SCHEMA = schemas.SystemicTherapyMedicationSchema
    CREATE_SCHEMA = schemas.SystemicTherapyMedicationCreateSchema

    def get_route_url(self, instance):
        return f"/{instance.systemic_therapy.id}/medications"

    def get_route_url_with_id(self, instance):
        return f"/{instance.systemic_therapy.id}/medications/{instance.id}"

    def get_route_url_history(self, instance):
        return (
            f"/{instance.systemic_therapy.id}/medications/{instance.id}/history/events"
        )

    def get_route_url_history_with_id(self, instance, event):
        return f"/{instance.systemic_therapy.id}/medications/{instance.id}/history/events/{event.pgh_id}"

    def get_route_url_history_revert(self, instance, event):
        return f"/{instance.systemic_therapy.id}/medications/{instance.id}/history/events/{event.pgh_id}/reversion"


class TestSurgeryController(CrudApiControllerTestCase):
    controller_path = "/api/v1/surgeries"
    FACTORY = factories.SurgeryFactory
    MODEL = models.Surgery
    SCHEMA = schemas.SurgerySchema
    CREATE_SCHEMA = schemas.SurgeryCreateSchema


class TestRadiotherapyController(CrudApiControllerTestCase):
    controller_path = "/api/v1/radiotherapies"
    FACTORY = factories.RadiotherapyFactory
    MODEL = models.Radiotherapy
    SCHEMA = schemas.RadiotherapySchema
    CREATE_SCHEMA = schemas.RadiotherapyCreateSchema


class TestRadiotherapyDosageController(CrudApiControllerTestCase):
    controller_path = "/api/v1/radiotherapies"
    FACTORY = factories.RadiotherapyDosageFactory
    MODEL = models.RadiotherapyDosage
    SCHEMA = schemas.RadiotherapyDosageSchema
    CREATE_SCHEMA = schemas.RadiotherapyDosageCreateSchema

    def get_route_url(self, instance):
        return f"/{instance.radiotherapy.id}/dosages"

    def get_route_url_with_id(self, instance):
        return f"/{instance.radiotherapy.id}/dosages/{instance.id}"

    def get_route_url_history(self, instance):
        return f"/{instance.radiotherapy.id}/dosages/{instance.id}/history/events"

    def get_route_url_history_with_id(self, instance, event):
        return f"/{instance.radiotherapy.id}/dosages/{instance.id}/history/events/{event.pgh_id}"

    def get_route_url_history_revert(self, instance, event):
        return f"/{instance.radiotherapy.id}/dosages/{instance.id}/history/events/{event.pgh_id}/reversion"


class TestRadiotherapySettingController(CrudApiControllerTestCase):
    controller_path = "/api/v1/radiotherapies"
    FACTORY = factories.RadiotherapySettingFactory
    MODEL = models.RadiotherapySetting
    SCHEMA = schemas.RadiotherapySettingSchema
    CREATE_SCHEMA = schemas.RadiotherapySettingCreateSchema

    def get_route_url(self, instance):
        return f"/{instance.radiotherapy.id}/settings"

    def get_route_url_with_id(self, instance):
        return f"/{instance.radiotherapy.id}/settings/{instance.id}"

    def get_route_url_history(self, instance):
        return f"/{instance.radiotherapy.id}/settings/{instance.id}/history/events"

    def get_route_url_history_with_id(self, instance, event):
        return f"/{instance.radiotherapy.id}/settings/{instance.id}/history/events/{event.pgh_id}"

    def get_route_url_history_revert(self, instance, event):
        return f"/{instance.radiotherapy.id}/settings/{instance.id}/history/events/{event.pgh_id}/reversion"


class TestTreatmentResponseController(CrudApiControllerTestCase):
    controller_path = "/api/v1/treatment-responses"
    FACTORY = factories.TreatmentResponseFactory
    MODEL = models.TreatmentResponse
    SCHEMA = schemas.TreatmentResponseSchema
    CREATE_SCHEMA = schemas.TreatmentResponseCreateSchema


class TestAdverseEventController(CrudApiControllerTestCase):
    controller_path = "/api/v1/adverse-events"
    FACTORY = factories.AdverseEventFactory
    MODEL = models.AdverseEvent
    SCHEMA = schemas.AdverseEventSchema
    CREATE_SCHEMA = schemas.AdverseEventCreateSchema


class TestAdverseEventSuspectedCauseController(CrudApiControllerTestCase):
    controller_path = "/api/v1/adverse-events"
    FACTORY = factories.AdverseEventSuspectedCauseFactory
    MODEL = models.AdverseEventSuspectedCause
    SCHEMA = schemas.AdverseEventSuspectedCauseSchema
    CREATE_SCHEMA = schemas.AdverseEventSuspectedCauseCreateSchema

    def get_route_url(self, instance):
        return f"/{instance.adverse_event.id}/suspected-causes"

    def get_route_url_with_id(self, instance):
        return f"/{instance.adverse_event.id}/suspected-causes/{instance.id}"

    def get_route_url_history(self, instance):
        return f"/{instance.adverse_event.id}/suspected-causes/{instance.id}/history/events"

    def get_route_url_history_with_id(self, instance, event):
        return f"/{instance.adverse_event.id}/suspected-causes/{instance.id}/history/events/{event.pgh_id}"

    def get_route_url_history_revert(self, instance, event):
        return f"/{instance.adverse_event.id}/suspected-causes/{instance.id}/history/events/{event.pgh_id}/reversion"


class TestAdverseEventMitigationController(CrudApiControllerTestCase):
    controller_path = "/api/v1/adverse-events"
    FACTORY = factories.AdverseEventMitigationFactory
    MODEL = models.AdverseEventMitigation
    SCHEMA = schemas.AdverseEventMitigationSchema
    CREATE_SCHEMA = schemas.AdverseEventMitigationCreateSchema

    def get_route_url(self, instance):
        return f"/{instance.adverse_event.id}/mitigations"

    def get_route_url_with_id(self, instance):
        return f"/{instance.adverse_event.id}/mitigations/{instance.id}"

    def get_route_url_history(self, instance):
        return f"/{instance.adverse_event.id}/mitigations/{instance.id}/history/events"

    def get_route_url_history_with_id(self, instance, event):
        return f"/{instance.adverse_event.id}/mitigations/{instance.id}/history/events/{event.pgh_id}"

    def get_route_url_history_revert(self, instance, event):
        return f"/{instance.adverse_event.id}/mitigations/{instance.id}/history/events/{event.pgh_id}/reversion"


class TestGenomicVariantController(CrudApiControllerTestCase):
    controller_path = "/api/v1/genomic-variants"
    FACTORY = factories.GenomicVariantFactory
    MODEL = models.GenomicVariant
    SCHEMA = schemas.GenomicVariantSchema
    CREATE_SCHEMA = schemas.GenomicVariantCreateSchema

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_gene_panels(self, scenario, config):
        self.controller_path = "/api/v1/autocomplete"
        factories.GenomicVariantFactory.create_batch(20)
        response = self.call_api_endpoint("GET", f"/gene-panels", **config)
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                list(
                    models.GenomicVariant.objects.values_list(
                        "gene_panel", flat=True
                    ).distinct()
                ),
            )


class TestTumorBoardController(CrudApiControllerTestCase):
    controller_path = "/api/v1/tumor-boards"
    FACTORY = [
        factories.TumorBoardFactory,
        factories.MolecularTumorBoardFactory,
    ]
    MODEL = [
        models.UnspecifiedTumorBoard,
        models.MolecularTumorBoard,
    ]
    SCHEMA = [
        schemas.UnspecifiedTumorBoardSchema,
        schemas.MolecularTumorBoardSchema,
    ]
    CREATE_SCHEMA = [
        schemas.UnspecifiedTumorBoardCreateSchema,
        schemas.MolecularTumorBoardCreateSchema,
    ]


class TestMolecularTherapeuticRecommendationController(CrudApiControllerTestCase):
    controller_path = "/api/v1/molecular-tumor-boards"
    FACTORY = factories.MolecularTherapeuticRecommendationFactory
    MODEL = models.MolecularTherapeuticRecommendation
    SCHEMA = schemas.MolecularTherapeuticRecommendationSchema
    CREATE_SCHEMA = schemas.MolecularTherapeuticRecommendationCreateSchema

    def get_route_url(self, instance):
        return f"/{instance.molecular_tumor_board.id}/therapeutic-recommendations"

    def get_route_url_with_id(self, instance):
        return f"/{instance.molecular_tumor_board.id}/therapeutic-recommendations/{instance.id}"

    def get_route_url_history(self, instance):
        return f"/{instance.molecular_tumor_board.id}/therapeutic-recommendations/{instance.id}/history/events"

    def get_route_url_history_with_id(self, instance, event):
        return f"/{instance.molecular_tumor_board.id}/therapeutic-recommendations/{instance.id}/history/events/{event.pgh_id}"

    def get_route_url_history_revert(self, instance, event):
        return f"/{instance.molecular_tumor_board.id}/therapeutic-recommendations/{instance.id}/history/events/{event.pgh_id}/reversion"


class TestTherapyLineController(CrudApiControllerTestCase):
    controller_path = "/api/v1/therapy-lines"
    FACTORY = factories.TherapyLineFactory
    MODEL = models.TherapyLine
    SCHEMA = schemas.TherapyLineSchema
    CREATE_SCHEMA = schemas.TherapyLineCreateSchema


class TestPerformanceStatusController(CrudApiControllerTestCase):
    controller_path = "/api/v1/performance-status"
    FACTORY = factories.PerformanceStatusFactory
    MODEL = models.PerformanceStatus
    SCHEMA = schemas.PerformanceStatusSchema
    CREATE_SCHEMA = schemas.PerformanceStatusCreateSchema


class TestLifestyleController(CrudApiControllerTestCase):
    controller_path = "/api/v1/lifestyles"
    FACTORY = factories.LifestyleFactory
    MODEL = models.Lifestyle
    SCHEMA = schemas.LifestyleSchema
    CREATE_SCHEMA = schemas.LifestyleCreateSchema


class TestFamilyHistoryController(CrudApiControllerTestCase):
    controller_path = "/api/v1/family-histories"
    FACTORY = factories.FamilyHistoryFactory
    MODEL = models.FamilyHistory
    SCHEMA = schemas.FamilyHistorySchema
    CREATE_SCHEMA = schemas.FamilyHistoryCreateSchema


class TestVitalsController(CrudApiControllerTestCase):
    controller_path = "/api/v1/vitals"
    FACTORY = factories.VitalsFactory
    MODEL = models.Vitals
    SCHEMA = schemas.VitalsSchema
    CREATE_SCHEMA = schemas.VitalsCreateSchema


class TestComorbiditiesAssessmentController(CrudApiControllerTestCase):
    controller_path = "/api/v1/comorbidities-assessments"
    FACTORY = factories.ComorbiditiesAssessmentFactory
    MODEL = models.ComorbiditiesAssessment
    SCHEMA = schemas.ComorbiditiesAssessmentSchema
    CREATE_SCHEMA = schemas.ComorbiditiesAssessmentCreateSchema

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_all_comorbidities_panels(self, scenario, config):
        response = self.call_api_endpoint("GET", "/meta/panels", **config)
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_comorbidities_panel_by_name(self, scenario, config):
        panel = "Charlson"
        response = self.call_api_endpoint("GET", f"/meta/panels/{panel}", **config)
        if scenario == "HTTPS Authenticated":
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["name"], panel)
            self.assertEqual(len(response.json()["categories"]), 16)


class TestGenomicSignatureController(CrudApiControllerTestCase):
    controller_path = "/api/v1/genomic-signatures"
    FACTORY = [
        factories.TumorMutationalBurdenFactory,
        factories.LossOfHeterozygosityFactory,
        factories.MicrosatelliteInstabilityFactory,
        factories.HomologousRecombinationDeficiencyFactory,
        factories.TumorNeoantigenBurdenFactory,
        factories.AneuploidScoreFactory,
    ]
    MODEL = [
        models.TumorMutationalBurden,
        models.LossOfHeterozygosity,
        models.MicrosatelliteInstability,
        models.HomologousRecombinationDeficiency,
        models.TumorNeoantigenBurden,
        models.AneuploidScore,
    ]
    SCHEMA = [
        schemas.TumorMutationalBurdenSchema,
        schemas.LossOfHeterozygositySchema,
        schemas.MicrosatelliteInstabilitySchema,
        schemas.HomologousRecombinationDeficiencySchema,
        schemas.TumorNeoantigenBurdenSchema,
        schemas.AneuploidScoreSchema,
    ]
    CREATE_SCHEMA = [
        schemas.TumorMutationalBurdenCreateSchema,
        schemas.LossOfHeterozygosityCreateSchema,
        schemas.MicrosatelliteInstabilityCreateSchema,
        schemas.HomologousRecombinationDeficiencyCreateSchema,
        schemas.TumorNeoantigenBurdenCreateSchema,
        schemas.AneuploidScoreCreateSchema,
    ]
