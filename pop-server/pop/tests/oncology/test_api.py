
from django.test import TestCase, Client
from django.db.models import Model
from ninja_extra.testing import TestClient
from pop.oncology import models, schemas
from pop.tests import factories 
from pop.core.schemas import ModelSchema 
from pop.core.controllers import AuthController 
from parameterized import parameterized, parameterized_class

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

class ApiControllerTestCase:
    CONTROLLER_BASE_URL: str
    FACTORY: factories.factory.django.DjangoModelFactory
    MODEL: Model
    SCHEMA: ModelSchema
    CREATE_SCHEMA: ModelSchema

    @classmethod
    def setUpTestData(cls):
        cls.maxDiff = None
        # Create a fake user
        cls.user = factories.UserFactory()
        cls.username = cls.user.username
        cls.password = faker.password()
        cls.user.set_password(cls.password)
        cls.user.save()
        # Ensure class settings are iterable
        cls.FACTORY = [cls.FACTORY] if not isinstance(cls.FACTORY, list) else cls.FACTORY
        cls.SUBTESTS = len(cls.FACTORY)
        cls.MODEL = [cls.MODEL]*cls.SUBTESTS if not isinstance(cls.MODEL, list) else cls.MODEL
        cls.SCHEMA = [cls.SCHEMA]*cls.SUBTESTS if not isinstance(cls.SCHEMA, list) else cls.SCHEMA
        cls.CREATE_SCHEMA = [cls.CREATE_SCHEMA]*cls.SUBTESTS if not isinstance(cls.CREATE_SCHEMA, list) else cls.CREATE_SCHEMA
        
    def get_route_url(self, instance):
        return f'/'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.id}'
        
    def _authenticate_user(self):
        # Login the user and retrieve the JWT token
        auth_client = TestClient(AuthController)
        response = auth_client.post(
            "/pair", 
            json={
                "username": self.username, 
                "password": self.password
            }, 
            secure=True)
        token = response.json()["access"]
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
        if response.status_code == 500:
            print(response.status_code)
        self.assertIn(
            response.status_code, 
            expected_responses, 
            f'Unexpected response status code: {response.status_code}'
        )
        return response

    def _remove_key_recursive(self, dictionary, keys_to_remove):
        """
        Recursively removes a key from a dictionary that contains lists.

        Args:
            dictionary (dict): The dictionary to remove the key from.
            key_to_remove (str): The key to remove.

        Returns:
            dict: The updated dictionary with the key removed.
        """
        def __remove_key_recursive(d, key_to_remove):
            for key, value in list(d.items()):
                if key == key_to_remove:
                    del d[key]
                elif isinstance(value, dict):
                    __remove_key_recursive(value, key_to_remove)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            __remove_key_recursive(item, key_to_remove)
            return d 
        for key_to_remove in keys_to_remove:
            dictionary = __remove_key_recursive(dictionary, key_to_remove)
        return dictionary

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_get_all(self, scenario, *config):            
        for i in range(self.SUBTESTS):
            instance = self.FACTORY[i](created_by=self.user)
            # Call the API endpoint
            response = self.call_api_endpoint(GET, self.get_route_url(instance), *config)
            with self.subTest(i=i):
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    self.assertEqual(response.status_code, 200)
                    if 'items' in response.json():
                        entry = response.json()['items'][0]
                    else:
                        entry = response.json()[0]
                    expected = self.SCHEMA[i].model_validate(instance).model_dump()
                    result = self.SCHEMA[i].model_validate(entry).model_dump()
                    expected = self._remove_key_recursive(expected, ['updatedAt', 'createdAt'])
                    result = self._remove_key_recursive(result, ['updatedAt', 'createdAt'])
                    self.assertEqual(expected, result)
                self.MODEL[i].objects.all().delete()

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_get_by_id(self, scenario, *config):              
        for i in range(self.SUBTESTS):
            instance = self.FACTORY[i](created_by=self.user)
            # Call the API endpoint
            response = self.call_api_endpoint(GET, self.get_route_url_with_id(instance), *config)
            with self.subTest(i=i):
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    self.assertEqual(response.status_code, 200)
                    expected = self.SCHEMA[i].model_validate(instance).model_dump()
                    result = self.SCHEMA[i].model_validate(response.json()).model_dump()
                    expected = self._remove_key_recursive(expected, ['updatedAt', 'createdAt'])
                    result = self._remove_key_recursive(result, ['updatedAt', 'createdAt'])
                    self.assertDictEqual(result, expected)
    
    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_delete(self, scenario, *config):              
        for i in range(self.SUBTESTS):
            instance = self.FACTORY[i](created_by=self.user)
            # Call the API endpoint
            response = self.call_api_endpoint(DELETE, self.get_route_url_with_id(instance), *config)
            with self.subTest(i=i):       
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    self.assertEqual(response.status_code, 204)
                    self.assertFalse(self.MODEL[i].objects.filter(id=instance.id).exists())

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_create(self, scenario, *config):                     
        for i in range(self.SUBTESTS):
            instance = self.FACTORY[i](created_by=self.user)
            json_data = self.CREATE_SCHEMA[i].model_validate(instance).model_dump(mode='json')
            # Call the API endpoint.
            response = self.call_api_endpoint(POST, self.get_route_url(instance), *config, data=json_data)
            with self.subTest(i=i):       
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    created_id = response.json()['id']
                    self.assertEqual(response.status_code, 201)
                    created_instance = self.MODEL[i].objects.filter(id=created_id).first()
                    self.assertIsNotNone(created_instance)
                    self.assertEqual(self.user,created_instance.created_by)
                    self.assertIn(self.user, created_instance.updated_by.all())

    @parameterized.expand(CONNECTION_SCENARIOS)
    def test_update(self, scenario, *config):                   
        for i in range(self.SUBTESTS):
            instance = self.FACTORY[i]()
            with self.subTest(i=i):           
                # Prepare the data
                creator = instance.created_by
                json_data = self.CREATE_SCHEMA[i].model_validate(instance).model_dump(mode='json')
                # Call the API endpoint
                response = self.call_api_endpoint(PUT, self.get_route_url_with_id(instance), *config, data=json_data)
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    self.assertEqual(response.status_code, 204) 
                    updated_instance =self.MODEL[i].objects.filter(id=instance.id).first() 
                    self.assertIsNotNone(updated_instance, 'The updated instance does not exist') 
                    self.assertEqual(creator, updated_instance.created_by) 
                    self.assertIn(self.user, updated_instance.updated_by.all()) 
               
                
    
class TestPatientCaseController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/patient-cases'
    FACTORY = factories.PatientCaseFactory
    MODEL = models.PatientCase
    SCHEMA = schemas.PatientCaseSchema
    CREATE_SCHEMA = schemas.PatientCaseCreateSchema             


class TestNeoplastcEntityController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/neoplastic-entities'
    FACTORY = factories.PrimaryNeoplasticEntityFactory
    MODEL = models.NeoplasticEntity
    SCHEMA = schemas.NeoplasticEntitySchema
    CREATE_SCHEMA = schemas.NeoplasticEntityCreateSchema    
    

class TestStagingController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/stagings'
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
    CREATE_SCHEMA = [
        schemas.TNMStagingCreateSchema, 
        schemas.FIGOStagingCreateSchema
    ]
    

class TestTumorMarkerController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/tumor-markers'
    FACTORY = factories.TumorMarkerTestFactory
    MODEL = models.TumorMarker
    SCHEMA = schemas.TumorMarkerSchema
    CREATE_SCHEMA = schemas.TumorMarkerCreateSchema    
    

class TestRiskAssessmentController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/risk-assessments'
    FACTORY = factories.RiskAssessmentFactory
    MODEL = models.RiskAssessment
    SCHEMA = schemas.RiskAssessmentSchema
    CREATE_SCHEMA = schemas.RiskAssessmentCreateSchema    
    
    
class TestSystemicTherapyController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/systemic-therapies'
    FACTORY = factories.SystemicTherapyFactory
    MODEL = models.SystemicTherapy
    SCHEMA = schemas.SystemicTherapySchema
    CREATE_SCHEMA = schemas.SystemicTherapyCreateSchema    
    
    
class TestSystemicTherapyMedicationController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/systemic-therapies'
    FACTORY = factories.SystemicTherapyMedicationFactory
    MODEL = models.SystemicTherapyMedication
    SCHEMA = schemas.SystemicTherapyMedicationSchema
    CREATE_SCHEMA = schemas.SystemicTherapyMedicationCreateSchema    

    def get_route_url(self, instance):
        return f'/{instance.systemic_therapy.id}/medications/'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.systemic_therapy.id}/medications/{instance.id}'

class TestSurgeryController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/surgeries'
    FACTORY = factories.SurgeryFactory
    MODEL = models.Surgery
    SCHEMA = schemas.SurgerySchema
    CREATE_SCHEMA = schemas.SurgeryCreateSchema    
    

    
class TestRadiotherapyController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/radiotherapies'
    FACTORY = factories.RadiotherapyFactory
    MODEL = models.Radiotherapy
    SCHEMA = schemas.RadiotherapySchema
    CREATE_SCHEMA = schemas.RadiotherapyCreateSchema    
    
class TestRadiotherapyDosageController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/radiotherapies'
    FACTORY = factories.RadiotherapyDosageFactory
    MODEL = models.RadiotherapyDosage
    SCHEMA = schemas.RadiotherapyDosageSchema
    CREATE_SCHEMA = schemas.RadiotherapyDosageCreateSchema    

    def get_route_url(self, instance):
        return f'/{instance.radiotherapy.id}/dosages/'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.radiotherapy.id}/dosages/{instance.id}'
    

class TestRadiotherapySettingController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/radiotherapies'
    FACTORY = factories.RadiotherapySettingFactory
    MODEL = models.RadiotherapySetting
    SCHEMA = schemas.RadiotherapySettingSchema
    CREATE_SCHEMA = schemas.RadiotherapySettingCreateSchema    

    def get_route_url(self, instance):
        return f'/{instance.radiotherapy.id}/settings/'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.radiotherapy.id}/settings/{instance.id}'
    
        
class TestGenomicVariantController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/genomic-variants'
    FACTORY = factories.GenomicVariantFactory
    MODEL = models.GenomicVariant
    SCHEMA = schemas.GenomicVariantSchema
    CREATE_SCHEMA = schemas.GenomicVariantCreateSchema    
    
        
class TestPerformanceStatusController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/performance-status'
    FACTORY = factories.PerformanceStatusFactory
    MODEL = models.PerformanceStatus
    SCHEMA = schemas.PerformanceStatusSchema
    CREATE_SCHEMA = schemas.PerformanceStatusCreateSchema    
    
    
class TestLifestyleController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/lifestyles'
    FACTORY = factories.LifestyleFactory
    MODEL = models.Lifestyle
    SCHEMA = schemas.LifestyleSchema
    CREATE_SCHEMA = schemas.LifestyleCreateSchema    
    
    
class TestFamilyHistoryController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/family-histories'
    FACTORY = factories.FamilyHistoryFactory
    MODEL = models.FamilyHistory
    SCHEMA = schemas.FamilyHistorySchema
    CREATE_SCHEMA = schemas.FamilyHistoryCreateSchema    


class TestComorbiditiesAssessmentController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/comorbidities-assessments'
    FACTORY = factories.ComorbiditiesAssessmentFactory
    MODEL = models.ComorbiditiesAssessment
    SCHEMA = schemas.ComorbiditiesAssessmentSchema
    CREATE_SCHEMA = schemas.ComorbiditiesAssessmentCreateSchema    


class TestGenomicSignatureController(ApiControllerTestCase, TestCase):
    CONTROLLER_BASE_URL = '/api/genomic-signatures'
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
    