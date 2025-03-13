from django.test import TestCase
from pop.tests import common, factories
from pop.oncology.models import PatientCase 
from pop.oncology.schemas.bundle import PatientCaseBundle
from parameterized import parameterized

from pop.core.measures import measures
from pop.core.measures.schemas import MeasureConversion   
   
class TestBundlesController(common.ApiControllerTestMixin, TestCase):
    controller_path = '/api/patient-cases/bundles'
    
    def setUp(self):
        super().setUp()
        self.case = factories.PatientCaseFactory.create()
        factories.PrimaryNeoplasticEntityFactory.create(case=self.case)
        factories.PrimaryNeoplasticEntityFactory.create(case=self.case)
        factories.SystemicTherapyFactory.create(case=self.case, therapy_line=None)
        self.case.save() 
        self.case.refresh_from_db() 
        self.bundle = PatientCaseBundle.model_validate(self.case)
        
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_export_case(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint('GET', f'/export/{self.case.id}', **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            entry = response.json()
            # Assert response content
            self.assertEqual(self.case.neoplastic_entities.all().count(), len(entry['neoplasticEntities']))
            self.assertEqual(self.case.systemic_therapies.all().count(), len(entry['systemicTherapies']))
            self.assertEqual(self.case.stagings.all().count(), len(entry['stagings']))
        # Clean-up
        PatientCase.objects.all().delete()

    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_import_case(self, scenario, config):
        self.case.delete()
        # Call the API endpoint
        response = self.call_api_endpoint('POST', '/import', data=self.bundle.model_dump(mode='json'), **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            # Assert resonse
            self.assertEqual(response.status_code, 201)
            self.assertEqual(self.case.clinical_identifier, PatientCase.objects.get(pseudoidentifier=self.bundle.pseudoidentifier).clinical_identifier)
        # Clean-up
        PatientCase.objects.all().delete()
