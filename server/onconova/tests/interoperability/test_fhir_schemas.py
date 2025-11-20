from django.test import TestCase
from ninja import Schema
from unittest.mock import patch
import json
from onconova.oncology import schemas
from onconova.interoperability.fhir import schemas as fhir
from onconova.tests import factories

from fhircraft.fhir.resources.datatypes.R4.complex import (
    Coding,
)


class TestFhirSchemas(TestCase):

    def _test_circular_mapping(self, schema: type[Schema], fhir_schema, factory):
        instance = factory.create()
        original_schema = schema.model_validate(instance)
        fhir_resource = fhir_schema.onconova_to_fhir(original_schema)
        new_schema = fhir_schema.fhir_to_onconova(fhir_resource)
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