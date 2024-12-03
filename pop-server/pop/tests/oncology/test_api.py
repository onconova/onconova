
from django.test import TestCase, Client
from ninja_extra.testing import TestClient
from pop.oncology import models, schemas
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

class ApiControllerTestCase(TestCase):
    CONTROLLER_BASE_URL: str
    
    @classmethod
    def setUpTestData(cls):
        cls.maxDiff = None
        # Create a fake user
        user = factories.UserFactory()
        cls.username = user.username
        cls.password = faker.password()
        user.set_password(cls.password)
        user.save()
        cls.user = user
        cls.case = factories.PatientCaseFactory(created_by=user)

    def _authenticate_user(self):
        # Login the user and retrieve the JWT token
        auth_client = TestClient(AuthController)
        response = auth_client.post(
            "/sliding", 
            json={
                "username": self.username, 
                "password": self.password
            }, 
            secure=True)
        token = response.json()["token"]
        return {"Authorization": f"Bearer {str(token)}"}

    def call_api_endpoint(self, verb, route, expected_responses, authenticate, secure, data=None):        
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
        response = action[verb](
            f'{self.CONTROLLER_BASE_URL}{route}', 
            secure=secure, 
            data=data if data is not None else None, 
            content_type="application/json"
        )
        self.assertIn(
            response.status_code, 
            expected_responses, 
            f'Unexpected response status code: {response.status_code}'
        )
        return response
    
    
    
    
class TestPatientCaseController(ApiControllerTestCase):
    CONTROLLER_BASE_URL = '/api/patient-cases'

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_get_patient_case_by_id(self, scenario, *config):        
        # Call the API endpoint
        response = self.call_api_endpoint(GET, f'/{self.case.id}', *config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 200)
            expected = schemas.PatientCaseSchema.model_validate(self.case).model_dump(exclude=['createdAt','updatedAt'])
            result = schemas.PatientCaseSchema.model_validate(response.json()).model_dump(exclude=['createdAt','updatedAt'])
            self.assertDictEqual(result, expected)
            self.assertEqual(self.user.id, result['createdById'])

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_get_all_patient_cases(self, scenario, *config):            
        # Call the API endpoint
        response = self.call_api_endpoint(GET, f'/', *config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 200)
            entry = response.json()['items'][0]
            expected = schemas.PatientCaseSchema.model_validate(self.case).model_dump(exclude=['createdAt','updatedAt'])
            result = schemas.PatientCaseSchema.model_validate(entry).model_dump(exclude=['createdAt','updatedAt'])
            self.assertEqual(expected, result)

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_delete_patient_case_by_id(self, scenario, *config):            
        # Call the API endpoint
        response = self.call_api_endpoint(DELETE, f'/{self.case.id}', *config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 204)
            self.assertFalse(models.PatientCase.objects.filter(id=self.case.id).exists())

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_create_patient_case(self, scenario, *config):            
        json_data = schemas.PatientCaseCreateSchema.model_validate(self.case).model_dump(mode='json')
        # Call the API endpoint
        response = self.call_api_endpoint(POST, f'/', *config, data=json_data)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            created_id = response.json()['id']
            self.assertEqual(response.status_code, 201)
            created_instance = models.PatientCase.objects.filter(id=created_id).first()
            self.assertIsNotNone(created_instance)
            self.assertEqual(self.user,created_instance.created_by)
            self.assertIn(self.user, created_instance.updated_by.all())

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_update_patient_case(self, scenario, *config):            
        # Prepare the data
        patient = factories.PatientCaseFactory.create()
        creator = patient.created_by
        json_data = schemas.PatientCaseCreateSchema.model_validate(patient).model_dump(mode='json')
        # Call the API endpoint
        response = self.call_api_endpoint(PUT, f'/{patient.id}', *config, data=json_data)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 204)
            updated_instance = models.PatientCase.objects.filter(id=patient.id).first()
            self.assertIsNotNone(updated_instance) 
            self.assertEqual(creator, updated_instance.created_by)
            self.assertIn(self.user, updated_instance.updated_by.all())
            


class TestNeoplastcEntityController(ApiControllerTestCase):
    CONTROLLER_BASE_URL = '/api/neoplastic-entities'
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cancer_entity = factories.PrimaryNeoplasticEntityFactory(case=cls.case)
        
    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_get_all_neoplastic_entities(self, scenario, *config):            
        # Call the API endpoint
        response = self.call_api_endpoint(GET, f'/', *config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 200)
            entry = response.json()[0]
            expected = schemas.NeoplasticEntitySchema.model_validate(self.cancer_entity).model_dump(exclude=['createdAt','updatedAt'])
            result = schemas.NeoplasticEntitySchema.model_validate(entry).model_dump(exclude=['createdAt','updatedAt'])
            self.assertEqual(expected, result)

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_get_neoplastic_entity_by_id(self, scenario, *config):        
        # Call the API endpoint
        response = self.call_api_endpoint(GET, f'/{self.cancer_entity.id}', *config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 200)
            expected = schemas.NeoplasticEntitySchema.model_validate(self.cancer_entity).model_dump(exclude=['createdAt','updatedAt'])
            result = schemas.NeoplasticEntitySchema.model_validate(response.json()).model_dump(exclude=['createdAt','updatedAt'])
            self.assertDictEqual(result, expected)
    
    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_delete_neoplastic_entity_by_id(self, scenario, *config):            
        # Call the API endpoint
        response = self.call_api_endpoint(DELETE, f'/{self.cancer_entity.id}', *config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 204)
            self.assertFalse(models.NeoplasticEntity.objects.filter(id=self.cancer_entity.id).exists())

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_create_neoplastic_entity(self, scenario, *config):            
        json_data = schemas.NeoplasticEntityCreateSchema.model_validate(self.cancer_entity).model_dump(mode='json')
        print(json_data)
        # Call the API endpoint.
        response = self.call_api_endpoint(POST, f'/', *config, data=json_data)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            created_id = response.json()['id']
            self.assertEqual(response.status_code, 201)
            created_instance = models.NeoplasticEntity.objects.filter(id=created_id).first()
            self.assertIsNotNone(created_instance)
            self.assertEqual(self.user,created_instance.created_by)
            self.assertIn(self.user, created_instance.updated_by.all())

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_update_neoplastic_entity(self, scenario, *config):            
        # Prepare the data
        instance = factories.PrimaryNeoplasticEntityFactory()
        creator = instance.created_by
        json_data = schemas.NeoplasticEntityCreateSchema.model_validate(instance).model_dump(mode='json')
        # Call the API endpoint
        response = self.call_api_endpoint(PUT, f'/{instance.id}', *config, data=json_data)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 204) 
            updated_instance = models.PatientCase.objects.filter(id=instance.id).first() 
            self.assertIsNotNone(updated_instance, 'The updated instance does not exist') 
            self.assertEqual(creator, updated_instance.created_by) 
            self.assertIn(self.user, updated_instance.updated_by.all()) 
            