from typing import Any
from django.test import TestCase
from ninja import Schema
from unittest.mock import patch
import json
from onconova.oncology import schemas
from onconova.interoperability.fhir import schemas as fhir
from onconova.tests import factories
from parameterized import parameterized
from fhircraft.fhir.resources.datatypes.R4.complex import (
    Coding,
)


class TestFhirSchemas(TestCase):

    def _test_circular_mapping(self, schema: type[Schema], fhir_schema, factory):
        instance = factory.create()
        original_schema = schema.model_validate(instance)
        fhir_resource = fhir_schema.onconova_to_fhir(original_schema)
        print(fhir_resource.model_dump_json(indent=2))
        new_schema = fhir_schema.fhir_to_onconova(fhir_resource)
        for child_instance, new_child_schema in fhir_schema.fhir_to_onconova_related(
            fhir_resource
        ):
            print(new_child_schema.model_dump_json(indent=2))
            new_child_schema.model_dump_django(instance=child_instance)
        new_instance = new_schema.model_dump_django(instance=instance)
        resulting_schema = schema.model_validate(new_instance)

        original_schema_dict = original_schema.model_dump(
            mode="json",
            exclude={"id", "createdAt", "updatedAt", "createdBy", "updatedBy"},
        )
        resulting_schema_dict = resulting_schema.model_dump(
            mode="json",
            exclude={"id", "createdAt", "updatedAt", "createdBy", "updatedBy"},
        )

        def _normalize_dict(data) -> Any:
            """Recursively remove audit fields and round floats to avoid precision errors."""
            if isinstance(data, dict):
                return {
                    k: _normalize_dict(v)
                    for k, v in data.items()
                    if k
                    not in {"id", "createdAt", "updatedAt", "createdBy", "updatedBy"}
                }
            elif isinstance(data, list):
                return [_normalize_dict(item) for item in data]
            elif isinstance(data, float):
                return round(data, 7)
            else:
                return data

        original_schema_dict = _normalize_dict(original_schema.model_dump(mode="json"))
        resulting_schema_dict = _normalize_dict(
            resulting_schema.model_dump(mode="json")
        )
        if original_schema_dict != resulting_schema_dict:
            print("Original Schema:")
            print(json.dumps(original_schema_dict, indent=2))
            print("Resulting Schema:")
            print(json.dumps(resulting_schema_dict, indent=2))
        self.assertDictEqual(original_schema_dict, resulting_schema_dict)

    @patch(
        "onconova.interoperability.fhir.schemas.cancer_patient.CancerPatientProfile._get_gender_codesystem",
        autospec=True,
        return_value="http://test.org/codesystem/administrativegender",
    )
    @patch(
        "onconova.interoperability.fhir.schemas.cancer_patient.CancerPatientProfile._get_birthsex_codesystem",
        autospec=True,
        return_value="http://test.org/codesystem/birthsex",
    )
    def test_cancer_patient_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.PatientCase,
            fhir.CancerPatientProfile,
            factories.PatientCaseFactory,
        )

    def test_primary_cancer_condition_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.NeoplasticEntity,
            fhir.PrimaryCancerConditionProfile,
            factories.PrimaryNeoplasticEntityFactory,
        )

    def test_secondary_cancer_condition_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.NeoplasticEntity,
            fhir.SecondaryCancerConditionProfile,
            factories.MetastaticNeoplasticEntityFactory,
        )

    @patch(
        "onconova.interoperability.fhir.schemas.tumor_marker.TumorMarkerProfile.map_to_fhir",
        autospec=True,
        return_value=Coding(
            code="9811-1",
            system="http://loinc.org",
            display="Chromogranin A [Mass/volume] in Serum or Plasma",
        ),
    )
    def test_tumor_marker_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.TumorMarker,
            fhir.TumorMarkerProfile,
            factories.TumorMarkerTestFactory,
        )

    def test_cancer_risk_assessment_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.RiskAssessment,
            fhir.CancerRiskAssessmentProfile,
            factories.RiskAssessmentFactory,
        )

    def test_genomic_variant_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.GenomicVariant,
            fhir.GenomicVariantProfile,
            factories.GenomicVariantFactory,
        )

    def test_tumor_mutational_burden_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.TumorMutationalBurden,
            fhir.TumorMutationalBurdenProfile,
            factories.TumorMutationalBurdenFactory,
        )

    def test_microsatellite_instability_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.MicrosatelliteInstability,
            fhir.MicrosatelliteInstabilityProfile,
            factories.MicrosatelliteInstabilityFactory,
        )

    def test_loss_of_heterozygosity_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.LossOfHeterozygosity,
            fhir.LossOfHeterozygosityProfile,
            factories.LossOfHeterozygosityFactory,
        )

    def test_homologous_recombination_deficiency_profile_schema_mappings(
        self, *args, **kwargs
    ):
        self._test_circular_mapping(
            schemas.HomologousRecombinationDeficiency,
            fhir.HomologousRecombinationDeficiencyProfile,
            factories.HomologousRecombinationDeficiencyFactory,
        )

    def test_tumor_neoantigen_burden_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.TumorNeoantigenBurden,
            fhir.TumorNeoantigenBurdenProfile,
            factories.TumorNeoantigenBurdenFactory,
        )

    def test_aneuploid_score_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.AneuploidScore,
            fhir.AneuploidScoreProfile,
            factories.AneuploidScoreFactory,
        )

    def test_comorbidities_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.ComorbiditiesAssessment,
            fhir.ComorbiditiesProfile,
            factories.ComorbiditiesAssessmentFactory,
        )

    def test_lifestyle_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.Lifestyle,
            fhir.LifestyleProfile,
            factories.LifestyleFactory,
        )

    def test_ecog_performance_status_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.PerformanceStatus,
            fhir.ECOGPerformanceStatusProfile,
            factories.ECOGPerformanceStatusFactory,
        )

    def test_karnofsky_performance_status_profile_schema_mappings(
        self, *args, **kwargs
    ):
        self._test_circular_mapping(
            schemas.PerformanceStatus,
            fhir.KarnofskyPerformanceStatusProfile,
            factories.KarnofskyPerformanceStatusFactory,
        )

    def test_imaging_disease_status_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.TreatmentResponse,
            fhir.ImagingDiseaseStatusProfile,
            factories.TreatmentResponseFactory,
        )

    @parameterized.expand(
        [
            (
                schemas.FIGOStaging,
                factories.FIGOStagingFactory,
            ),
            (
                schemas.RaiStaging,
                factories.RaiStagingFactory,
            ),
            (
                schemas.BreslowDepth,
                factories.BreslowDepthFactory,
            ),
            (
                schemas.BinetStaging,
                factories.BinetStagingFactory,
            ),
            (
                schemas.ClarkStaging,
                factories.ClarkStagingFactory,
            ),
            (
                schemas.ISSStaging,
                factories.ISSStagingFactory,
            ),
            (
                schemas.RISSStaging,
                factories.RISSStagingFactory,
            ),
            (
                schemas.INSSStage,
                factories.INSSStagingFactory,
            ),
            (
                schemas.INRGSSStage,
                factories.INRGSSStagingFactory,
            ),
            (
                schemas.GleasonGrade,
                factories.GleasonGradeFactory,
            ),
            (
                schemas.RhabdomyosarcomaClinicalGroup,
                factories.RhabdomyosarcomaClinicalGroupFactory,
            ),
            (
                schemas.WilmsStage,
                factories.WilmsStageFactory,
            ),
        ]
    )
    def test_cancer_stage_profile_schema_mappings(
        self, schema, factory, *args, **kwargs
    ):
        self._test_circular_mapping(schema, fhir.CancerStageProfile, factory)

    def test_tnm_stage_group_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.TNMStaging,
            fhir.TNMStageGroupProfile,
            factories.TNMStagingFactory,
        )

    def test_lymphoma_stage_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.LymphomaStaging,
            fhir.LymphomaStageProfile,
            factories.LymphomaStagingFactory,
        )

    def test_surgery_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.Surgery,
            fhir.SurgicalProcedureProfile,
            factories.SurgeryFactory,
        )

    def test_radiotherapy_course_summary_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.Radiotherapy,
            fhir.RadiotherapyCourseSummaryProfile,
            factories.RadiotherapyFactory,
        )

    def test_tumor_board_review_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.UnspecifiedTumorBoard,
            fhir.TumorBoardReviewProfile,
            factories.TumorBoardFactory,
        )

    def test_molecular_tumor_board_review_profile_schema_mappings(
        self, *args, **kwargs
    ):
        self._test_circular_mapping(
            schemas.MolecularTumorBoard,
            fhir.MolecularTumorBoardReviewProfile,
            factories.MolecularTumorBoardFactory,
        )

    def test_adverse_event_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.AdverseEvent,
            fhir.AdverseEventProfile,
            factories.AdverseEventFactory,
        )

    def test_cancer_family_member_history_profile_schema_mappings(
        self, *args, **kwargs
    ):
        self._test_circular_mapping(
            schemas.FamilyHistory,
            fhir.CancerFamilyMemberHistoryProfile,
            factories.FamilyHistoryFactory,
        )

    def test_medication_administration_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.SystemicTherapy,
            fhir.MedicationAdministrationProfile,
            factories.SystemicTherapyFactory,
        )

    def test_vitals_panel_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.Vitals,
            fhir.VitalsPanelProfile,
            factories.VitalsFactory,
        )

    def test_therapy_line_profile_schema_mappings(self, *args, **kwargs):
        self._test_circular_mapping(
            schemas.TherapyLine,
            fhir.TherapyLineProfile,
            factories.TherapyLineFactory,
        )
