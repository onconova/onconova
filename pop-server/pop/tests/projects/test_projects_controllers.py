from pop.tests.oncology.test_oncology_controllers import ApiControllerTextMixin
from django.test import TestCase
from pop.projects import schemas, models
from pop.tests import factories, common 
from parameterized import parameterized

class TestProjectController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/projects'
    FACTORY = factories.ProjectFactory
    MODEL = models.Project
    SCHEMA = schemas.ProjectSchema
    CREATE_SCHEMA = schemas.ProjectCreateSchema             


class TestProjectDataManagerController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/projects'
    FACTORY = factories.ProjectDataManagerGrantFactory
    MODEL = models.ProjectDataManagerGrant
    SCHEMA = schemas.ProjectDataManagerGrantSchema
    CREATE_SCHEMA = schemas.ProjectDataManagerGrantCreateSchema             

    HAS_UPDATE_ENDPOINT = False
    
    def get_route_url(self, instance):
        return f'/{instance.project.id}/members/{instance.member.id}/data-management/grants'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.project.id}/members/{instance.member.id}/data-management/grants/{instance.id}'
    
    def get_route_url_history(self, instance):
        return f'/{instance.project.id}/members/{instance.member.id}/data-management/grants/{instance.id}/history/events'
    
    def get_route_url_history_with_id(self, instance, event):
        return f'/{instance.project.id}/members/{instance.member.id}/data-management/grants/{instance.id}/history/events/{event.pgh_id}'
    
    def get_route_url_history_revert(self, instance, event):
        return f'/{instance.project.id}/members/{instance.member.id}/data-management/grants/{instance.id}/history/events/{event.pgh_id}/reversion'

    
    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_delete(self, scenario, config):         
        for i in range(self.SUBTESTS):
            instance = self.INSTANCE[i]
            config = {**config, 'expected_responses': (201, 403, 401, 301)}
            # Call the API endpoint
            response = self.call_api_endpoint('DELETE', self.get_route_url_with_id(instance), **config)
            with self.subTest(i=i):       
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    self.assertEqual(response.status_code, 201)
                    instance = self.MODEL[i].objects.filter(id=instance.id).first()
                    self.assertIsNotNone(instance)
                    self.assertTrue(instance.revoked)