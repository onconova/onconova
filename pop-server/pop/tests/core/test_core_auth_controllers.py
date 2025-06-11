
from django.test import TestCase
from pop.tests import common, factories
from pop.core.auth.models import User 
from pop.core.auth.schemas import UserSchema, UserCreateSchema, UserProfileSchema, UserPasswordReset
from parameterized import parameterized

from pop.core.measures import measures
from pop.core.measures.schemas import MeasureConversion   
   
class TestUserController(common.ApiControllerTestMixin, TestCase):
    controller_path = '/api/users'
    
    @classmethod 
    def setUpTestData(cls):
        super().setUpTestData()
        cls.instance = factories.UserFactory()
    
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_all_users(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint('GET', self.get_route_url(self.instance), **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            entry = response.json()['items'][0]
            # Assert response content
            expected = UserSchema.model_validate(self.instance).model_dump()
            result = UserSchema.model_validate(entry).model_dump()
            self.assertEqual(expected, result)


    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_user_by_id(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint('GET', self.get_route_url_with_id(self.instance), **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            entry = response.json()
            # Assert response content
            expected = UserSchema.model_validate(self.instance).model_dump()
            result = UserSchema.model_validate(entry).model_dump()
            self.assertEqual(expected, result)

    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_create_user_by_id(self, scenario, config):
        json_data = UserCreateSchema.model_validate(self.instance).model_dump(mode='json')
        json_data['username'] = 'new_username'
        # Call the API endpoint.
        response = self.call_api_endpoint('POST', self.get_route_url(self.instance), data=json_data, **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            new_user = User.objects.get(id=response.json()['id'])
            self.assertEqual('new_username', new_user.username)


    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_update_user_and_access_level(self, scenario, config):
        update_schema = UserCreateSchema.model_validate(self.instance)
        update_schema.accessLevel = 5
        json_data = update_schema.model_dump(mode='json')
        # Call the API endpoint.
        response = self.call_api_endpoint('PUT', self.get_route_url_with_id(self.instance), data=json_data, **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            updated_instance = User.objects.get(id=response.json()['id'])
            self.assertEqual(updated_instance.access_level, 5) 


    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_update_user_profile(self, scenario, config):
        new_first_name = 'John'
        new_last_name = 'Doe' 
        json_data = UserProfileSchema(firstName=new_first_name, lastName=new_last_name, email=self.instance.email).model_dump(mode='json')
        # Call the API endpoint.
        response = self.call_api_endpoint('PUT', f'/{self.instance.id}/profile', data=json_data, **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            updated_instance = User.objects.get(id=response.json()['id'])
            self.assertEqual(updated_instance.first_name, new_first_name) 
            self.assertEqual(updated_instance.last_name, new_last_name) 


    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_update_own_profile(self, scenario, config):
        new_config = {**config, 'access_level': 1}
        new_first_name = 'John'
        new_last_name = 'Doe' 
        json_data = UserProfileSchema(firstName=new_first_name, lastName=new_last_name, email=self.user.email).model_dump(mode='json')
        # Call the API endpoint.
        self.call_api_endpoint('PUT', f'/{self.user.id}/profile', data=json_data, **new_config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.user.refresh_from_db()
            self.assertEqual(self.user.first_name, new_first_name) 
            self.assertEqual(self.user.last_name, new_last_name) 
        
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_update_own_password(self, scenario, config):
        new_config = {**config, 'access_level': 1}
        old_password = 'oldPassword123'
        new_password = 'newPassword123'
        self.user.set_password(old_password)
        self.user.save()
        payload = UserPasswordReset(oldPassword=old_password, newPassword=new_password).model_dump(mode='json')
        # Call the API endpoint.
        self.call_api_endpoint('PUT', f'/{self.user.id}/password', data=payload, **new_config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            self.user.refresh_from_db()
            self.assertFalse(self.user.check_password(old_password))
            self.assertTrue(self.user.check_password(new_password))
        
        


class TestMeasuresController(common.ApiControllerTestMixin, TestCase):
    controller_path = '/api/measures'
    
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_measure_units(self, scenario, config):
        measure = measures.Volume
        # Call the API endpoint
        response = self.call_api_endpoint('GET', f'/{measure.__name__}/units', **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(measure.get_units().keys()), response.json())
            
            
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_measure_default_units(self, scenario, config):
        measure = measures.Volume
        # Call the API endpoint
        response = self.call_api_endpoint('GET', f'/{measure.__name__}/units/default', **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            self.assertEqual(measure.STANDARD_UNIT, response.json())
            
            
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_convert_units(self, scenario, config):
        measure = measures.Mass
        data = MeasureConversion(value=1, unit='kg', newUnit='g').model_dump(mode='json')
        # Call the API endpoint
        response = self.call_api_endpoint('POST', f'/{measure.__name__}/units/conversion', data=data, **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            # Assert resonse status
            converted_measure = response.json()
            self.assertEqual(converted_measure['unit'], 'g')
            self.assertEqual(converted_measure['value'], 1000)