
from django.test import TestCase, Client
from ninja_extra.testing import TestClient
from pop.oncology import models
from pop.oncology.controllers.CancerPatientController import CancerPatientController, CancerPatientCreateSchema, CancerPatientSchema
from pop.tests import factories 
from pop.core.controllers import AuthController 
from parameterized import parameterized

import faker 
faker = faker.Faker()

CONNECTION_SCENARIOS = [
    ('HTTPS Authenticated',    (200, 204, 201), True, True),
    ('HTTP Authenticated',     (301,), True, False),
    ('HTTPS Unauthenticated',  (401,), False, True),
    ('HTTP Unauthenticated',   (301,), False, False),
]
GET = 'get'
DELETE = 'delete'
PUT = 'put'
POST = 'post'

class TestCancerPatientController(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a fake user
        user = factories.UserFactory()
        cls.username = user.username
        cls.password = faker.password()
        user.set_password(cls.password)
        user.save()
        cls.patient = factories.CancerPatientFactory.create()
    
    def _authenticate_user(self):
        # Login the user and retrieve the JWT token
        auth_client = TestClient(AuthController)
        response = auth_client.post("/login", json={"username": self.username, "password": self.password}, secure=True)
        token = response.json()["token"]
        return {"Authorization": f"Bearer {str(token)}"}


    def _call_api_endpoint(self, verb, endpoint, expected_responses, authenticate, secure, data=None):        
        # Login the fake user and retrieve the JWT token
        auth_header = self._authenticate_user() if authenticate else {}
        # Prepare the controller
        client = Client(headers=auth_header)
        action = {
            POST: client.post,
            GET: client.get,
            PUT: client.put,
            DELETE: client.delete,
        }
        print(data)
        response = action[verb](endpoint, secure=secure, data=data if data is not None else None, content_type="application/json")
        self.assertIn(response.status_code, expected_responses, f'Unexpected response status code: {response.status_code}')
        return response

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_get_cancer_patient_by_id(self, _, *scenario):        
        response = self._call_api_endpoint(GET, f'/api/cancer-patients/{self.patient.id}', *scenario)
        if response == '200':
            expected = CancerPatientSchema.model_validate(self.patient).model_dump(exclude=['created_at','updated_at'])
            result = CancerPatientSchema.model_validate(response.json()).model_dump(exclude=['created_at','updated_at'])
            self.maxDiff = None
            self.assertDictEqual(result, expected)

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_get_all_cancer_patients(self, _, *scenario):            
        response = self._call_api_endpoint(DELETE, f'/api/cancer-patients/{self.patient.id}', *scenario)
        if response == '204':
            for entry in response.json()['items']:
                result = CancerPatientSchema.model_validate(entry).model_dump(exclude=['created_at','updated_at'])

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_delete_cancer_patient_by_id(self, _, *scenario):            
        response = self._call_api_endpoint(DELETE, f'/api/cancer-patients/{self.patient.id}', *scenario)
        if response == '204':
            self.assertFalse(models.CancerPatient.objects.filter(id=self.patient.id).exists())

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_create_cancer_patient(self, _, *scenario):            
        json_data = CancerPatientCreateSchema.model_validate(self.patient).model_dump(mode='json')
        response = self._call_api_endpoint(POST, f'/api/cancer-patients/', *scenario, data=json_data)
        if response == '201':
            self.assertTrue(models.CancerPatient.objects.filter(id=self.patient.id).exists())


    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_update_cancer_patient(self, _, *scenario):            
        patient = factories.CancerPatientFactory.create()
        json_data = CancerPatientCreateSchema.model_validate(patient).model_dump(mode='json')
        response = self._call_api_endpoint(PUT, f'/api/cancer-patients/{patient.id}', *scenario, data=json_data)
        if response == '201':
            self.assertTrue(models.CancerPatient.objects.filter(id=patient.id).exists()) 