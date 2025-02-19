
from django.test import TestCase
from pop.tests import common, factories
from pop.core.models import User 
from pop.core.schemas import UserSchema, UserCreateSchema, UserProfileSchema
from parameterized import parameterized

from pop.core.measures import measures
from pop.core.measures.schemas import MeasureConversion   
   
class TestUserController(common.ApiControllerTestMixin, TestCase):
    controller_path = '/api/auth/users'
    
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_all_users(self, scenario, config):
        instance = factories.UserFactory()
        # Call the API endpoint
        response = self.call_api_endpoint('GET', self.get_route_url(instance), **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            entry = response.json()['items'][0]
            # Assert response content
            expected = UserSchema.model_validate(instance).model_dump()
            result = UserSchema.model_validate(entry).model_dump()
            self.assertEqual(expected, result)
        # Clean-up
        User.objects.all().delete()


    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_user_by_id(self, scenario, config):
        instance = factories.UserFactory()
        # Call the API endpoint
        response = self.call_api_endpoint('GET', self.get_route_url_with_id(instance), **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            entry = response.json()
            # Assert response content
            expected = UserSchema.model_validate(instance).model_dump()
            result = UserSchema.model_validate(entry).model_dump()
            self.assertEqual(expected, result)
        # Clean-up
        User.objects.all().delete()


    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_create_user_by_id(self, scenario, config):
        instance = factories.UserFactory()
        json_data = UserCreateSchema.model_validate(instance).model_dump(mode='json')
        json_data['username'] = 'new_username'
        # Call the API endpoint.
        response = self.call_api_endpoint('POST', self.get_route_url(instance), data=json_data, **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            new_user = User.objects.get(id=response.json()['id'])
            self.assertEqual('new_username', new_user.username)
        # Clean-up
        User.objects.all().delete()


    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_update_user_and_access_level(self, scenario, config):
        instance = factories.UserFactory.create(access_level=1)
        update_schema = UserCreateSchema.model_validate(instance)
        update_schema.accessLevel = 5
        json_data = update_schema.model_dump(mode='json')
        # Call the API endpoint.
        response = self.call_api_endpoint('PUT', self.get_route_url_with_id(instance), data=json_data, **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            updated_instance = User.objects.get(id=response.json()['id'])
            self.assertEqual(updated_instance.access_level, 5) 
        # Clean-up
        User.objects.all().delete()


    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_update_user_profile(self, scenario, config):
        instance = factories.UserFactory()
        new_first_name = 'John'
        new_last_name = 'Doe' 
        json_data = UserProfileSchema(firstName=new_first_name, lastName=new_last_name, email=instance.email).model_dump(mode='json')
        # Call the API endpoint.
        response = self.call_api_endpoint('PUT', f'/{instance.id}/profile', data=json_data, **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            updated_instance = User.objects.get(id=response.json()['id'])
            self.assertEqual(updated_instance.first_name, new_first_name) 
            self.assertEqual(updated_instance.last_name, new_last_name) 
        # Clean-up
        User.objects.all().delete()


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
        # Clean-up
        User.objects.all().delete()
        
        


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
        data = MeasureConversion(value=1, unit='kg', new_unit='g').model_dump(mode='json')
        # Call the API endpoint
        response = self.call_api_endpoint('POST', f'/{measure.__name__}/units/conversion', data=data, **config)
        # Assert response content
        if scenario == 'HTTPS Authenticated':
            # Assert resonse status
            converted_measure = response.json()
            self.assertEqual(converted_measure['unit'], 'g')
            self.assertEqual(converted_measure['value'], 1000)