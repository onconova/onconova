from pop.tests.oncology.test_oncology_controllers import ApiControllerTextMixin
from django.test import TestCase
from pop.analytics import schemas, models
from pop.tests import factories 



    
class TestCohortController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/cohorts'
    FACTORY = factories.CohortFactory
    MODEL = models.Cohort
    SCHEMA = schemas.CohortSchema
    CREATE_SCHEMA = schemas.CohortCreateSchema             
