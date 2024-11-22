
from django.test import TestCase
from ninja.testing import TestClient
from pop.oncology.api import api, CancerPatientOut
from pop.tests.factories import CancerPatientFactory

class TestAPI(TestCase):

    def test_get_cancer_patient_by_id(self):
        patient = CancerPatientFactory()
        client = TestClient(api)
        response = client.get(f"/cancer-patients/{patient.id}")        
        self.assertEqual(response.status_code, 200)
        expected = CancerPatientOut.model_validate(patient).model_dump(exclude=['created_at','updated_at'])
        result = CancerPatientOut.model_validate(response.json()).model_dump(exclude=['created_at','updated_at'])
        self.maxDiff = None
        self.assertDictEqual(result, expected)

