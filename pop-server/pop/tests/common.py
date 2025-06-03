from django.db import connection
from django.db.models.base import ModelBase
from django.test import TestCase, Client
from urllib.parse import urlencode

class AbstractModelMixinTestCase(TestCase):
    """
    Abstract test case for mixin class.
    """

    mixin = None
    model = None

    @classmethod
    def setUpClass(cls) -> None:
        """Create a test model from the mixin"""
        class Meta:
            """Meta options for the temporary model"""
            app_label = 'test'
        cls.model = ModelBase(
            "Test" + cls.mixin.__name__,
            (cls.mixin,),
            {
                "__module__": cls.mixin.__module__,
                "Meta":Meta,
            }
        )

        with connection.schema_editor() as editor:
            editor.create_model(cls.model)

        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        """Delete the test model"""
        super().tearDownClass()

        with connection.schema_editor() as editor:
            editor.delete_model(cls.model)

        connection.close()




import uuid
from django.test import TestCase, Client
from ninja_extra.testing import TestClient
from pop.tests import factories 
from pop.core.controllers import AuthController 
from pop.core.models import User 
from faker import Faker

class ApiControllerTestMixin:
    
    # Properties
    controller_path: str
    scenarios = [
        ('HTTPS Authenticated', dict(expected_responses=(200, 204, 201), authenticated=True, use_https=True, access_level=5)),
        ('HTTP Authenticated', dict(expected_responses=(301,), authenticated=True, use_https=False, access_level=5)),
        ('HTTPS Unauthenticated', dict(expected_responses=(401,), authenticated=False, use_https=True, access_level=5)),
        ('HTTP Unauthenticated', dict(expected_responses=(301,), authenticated=False, use_https=False, access_level=5)),
        ('HTTPS Unauthorized', dict(expected_responses=(403,), authenticated=True, use_https=True, access_level=1)),
    ]
    get_scenarios = scenarios[:-1]
    
    @classmethod
    def setUpTestData(cls):
        cls.maxDiff = None
        # Generate user credentials
        username = f'user-{uuid.uuid4()}'
        password = Faker().password()
        # Create a fake user with known credentials if not exists
        cls.user = User.objects.filter(username=username).first()
        if not cls.user:
            cls.user = factories.UserFactory.create(username=username)
        cls.user.set_password(password)
        cls.user.save()
        # Authenticate user and get authentication HTTP header
        cls.auth_header = cls._authenticate_user_and_get_authentication_header(username, password)
        cls.authenticated_client = Client(headers=cls.auth_header)
        cls.unauthenticated_client = Client()
        
    def get_route_url(self, instance):
        return f''
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.id}'
    
    def get_route_url_history(self, instance):
        return f'/{instance.id}/history/events'
    
    def get_route_url_history_with_id(self, instance, event):
        return f'/{instance.id}/history/events/{event.pgh_id}'
    
    def get_route_url_history_revert(self, instance, event):
        return f'/{instance.id}/history/events/{event.pgh_id}/reversion'

    @staticmethod
    def _authenticate_user_and_get_authentication_header(username, password):
        # Login the user and retrieve the JWT token
        auth_client = Client()
        response = auth_client.post("/api/auth/session", data={'username': username, 'password': password}, content_type='application/json', secure=True)
        if response.status_code != 200:
            raise RuntimeError(f'Failed to authenticate user. Login endpoint returned {response.status_code}')
        token = response.json()['sessionToken']
        return {"X-Session-Token": str(token)}


    def call_api_endpoint(self, verb, route, expected_responses, authenticated, use_https, access_level, anonymized=None, data=None):        
        # Set the user access level for this call
        self.user.access_level = access_level
        self.user.save()
        # Prepare the controller
        client = self.authenticated_client if authenticated else self.unauthenticated_client
        action = {
            'POST': client.post,
            'GET': client.get,
            'PUT': client.put,
            'DELETE': client.delete,
        }
        queryparams = f'?{urlencode({"anonymized": anonymized})}' if verb=='GET' and anonymized is not None else ''
        print('URL',  f'{self.controller_path}{route}' + queryparams)
        response = action[verb](
            f'{self.controller_path}{route}' + queryparams, 
            secure=use_https, 
            data=data if data is not None else None, 
            content_type="application/json"
        )
        # Assert that there were no errors
        if response.status_code == 500:
            raise RuntimeError('An error ocurred during the API call (returned 500)')
        
        # Assert response status code
        self.assertIn(
            response.status_code, 
            expected_responses, 
            f'Endpoint responded with {response.status_code}'
        )
        return response