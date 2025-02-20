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


    
class TestDatasetController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/datasets'
    FACTORY = factories.DatasetFactory
    MODEL = models.Dataset
    SCHEMA = schemas.Dataset
    CREATE_SCHEMA = schemas.DatasetCreate             
