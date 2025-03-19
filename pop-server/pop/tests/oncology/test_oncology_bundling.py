from django.test import TestCase
from pop.tests import common, factories
from pop.oncology.models import PatientCase 
from pop.oncology.schemas.bundle import PatientCaseBundle
from parameterized import parameterized

from pop.core.measures import measures
from pop.core.measures.schemas import MeasureConversion   
   
class TestBundlesController(common.ApiControllerTestMixin, TestCase):
    controller_path = '/api/patient-cases/bundles'
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.case = factories.PatientCaseFactory.create()
        factories.PrimaryNeoplasticEntityFactory.create(case=cls.case)
        factories.SystemicTherapyFactory.create(case=cls.case, therapy_line=None)
        cls.case.save() 
        cls.case.refresh_from_db() 
        cls.bundle = PatientCaseBundle.model_validate(cls.case)
        cls.payload = cls.bundle.model_dump(mode='json')
        
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_export_case(self, scenario, config):
        response = self.call_api_endpoint('GET', f'/export/{self.case.id}', **config)
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 200)
            entry = response.json()
            self.assertEqual(self.case.neoplastic_entities.all().count(), len(entry['neoplasticEntities']))
            self.assertEqual(self.case.systemic_therapies.all().count(), len(entry['systemicTherapies']))
            self.assertEqual(self.case.stagings.all().count(), len(entry['stagings']))


    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_import_case(self, scenario, config):
        self.case.delete()
        response = self.call_api_endpoint('POST', '/import', data=self.payload, **config)
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 201)
            self.assertEqual(self.case.clinical_identifier, PatientCase.objects.get(pseudoidentifier=self.bundle.pseudoidentifier).clinical_identifier)


    def test_import_conflicting_case_unresolved(self):
        response = self.call_api_endpoint('POST', '/import', data=self.payload, expected_responses=[422], authenticated=True, use_https=True, access_level=5)
        self.assertEqual(response.status_code, 422)

    def test_import_conflicting_case_overwrite(self):
        response = self.call_api_endpoint('POST', '/import?conflict=overwrite', data=self.payload, expected_responses=[201], authenticated=True, use_https=True, access_level=5)
        self.assertEqual(response.status_code, 201)
        new_case = PatientCase.objects.get(pseudoidentifier=self.bundle.pseudoidentifier)
        self.assertEqual(self.case.clinical_identifier, new_case.clinical_identifier)
        self.assertNotEqual(self.case.id, new_case.id)
        self.assertIsNone(PatientCase.objects.filter(id=self.case.id).first())
        
    def test_import_conflicting_case_reassign(self):
        self.payload['clinicalIdentifier'] = '123456789'
        response = self.call_api_endpoint('POST', '/import?conflict=reassign', data=self.payload, expected_responses=[201], authenticated=True, use_https=True, access_level=5)
        self.assertEqual(response.status_code, 201)
        new_case = PatientCase.objects.get(clinical_identifier='123456789')
        self.assertNotEqual(self.case.clinical_identifier, new_case.clinical_identifier)
        self.assertNotEqual(self.case.id, new_case.id)
        self.assertIsNotNone(PatientCase.objects.filter(id=self.case.id).first())

    def test_import_conflicting_reassign_but_conflicting_clinical_identifier(self):
        response = self.call_api_endpoint('POST', '/import?conflict=reassign', data=self.payload, expected_responses=[422], authenticated=True, use_https=True, access_level=5)
        self.assertEqual(response.status_code, 422)