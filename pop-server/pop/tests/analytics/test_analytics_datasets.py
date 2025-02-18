

from django.test import TestCase
from pop.tests import factories

from pop.analytics.models import Cohort 
import pop.oncology.models as models


from pop.analytics.schemas import DatasetRule
from pop.analytics.datasets import construct_dataset
   
class TestConstructDataset(TestCase):

    def setUp(self):
        self.case = factories.PatientCaseFactory()
        self.cohort = Cohort.objects.create(name='test_cohort')
        self.cohort.cases.set([self.case])        


    def test_basic_dataset(self):
        rule = DatasetRule(resource='PatientCase', field='id')
        dataset = construct_dataset(self.cohort, [rule])
        self.assertEqual(self.case.id, dataset[0].get(rule.field))

    def test_query_date_field(self):
        rule = DatasetRule(resource='PatientCase', field='dateOfBirth')
        dataset = construct_dataset(self.cohort, [rule])
        self.assertEqual(self.case.created_at, dataset[0].get(rule.field))       
        
    def test_query_coded_concept_field(self):
        rule = DatasetRule(resource='PatientCase', field='gender')
        dataset = construct_dataset(self.cohort, [rule])
        self.assertEqual(self.case.gender.display, dataset[0].get(rule.field))     
        
    def test_case_pseudoidentifier_always_contained(self):
        rule = DatasetRule(resource='PatientCase', field='id')
        dataset = construct_dataset(self.cohort, [rule])
        self.assertIn('pseudoidentifier', dataset[0])
        self.assertEqual(self.case.pseudoidentifier, dataset[0].get('pseudoidentifier'))