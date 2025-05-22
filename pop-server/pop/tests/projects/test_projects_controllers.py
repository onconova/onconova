from pop.tests.oncology.test_oncology_controllers import ApiControllerTextMixin
from django.test import TestCase
from pop.projects import schemas, models
from pop.tests import factories

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
    history_tracked = False
    
    def get_route_url(self, instance):
        return f'/{instance.project.id}/members/{instance.member.id}/data-management/grants'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.project.id}/members/{instance.member.id}/data-management/grants/{instance.id}'
    