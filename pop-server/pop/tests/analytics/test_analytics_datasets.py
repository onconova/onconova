

from django.test import TestCase
from unittest.mock import MagicMock

from django.db.models import Subquery
from django.db.models import F 
from django_mock_queries.query import MockModel
from django.db.models.functions import JSONObject
from django.contrib.postgres.aggregates import ArrayAgg
from pydantic import ValidationError
from pop.tests import factories
import pop.oncology.models as models
from pop.analytics.models import Cohort 
from pop.analytics.schemas import DatasetRule
from pop.analytics.datasets import DatasetRuleProcessingError, DatasetRuleProcessor, construct_dataset, AggregationNode, AnnotationNode, AnnotationCompiler
   

class TestConstructDataset(TestCase):

    def setUp(self):
        self.case = factories.PatientCaseFactory()
        self.cohort = Cohort.objects.create(name='test_cohort')
        self.cohort.cases.set([self.case])        


    def test_basic_dataset(self):
        rule = DatasetRule(resource='PatientCase', field='id')
        dataset = construct_dataset(self.cohort, [rule])[0]
        self.assertEqual(self.case.id, dataset.get('id'))

    def test_query_multiple_fields(self):
        rules = [
            DatasetRule(resource='PatientCase', field='dateOfBirth'),
            DatasetRule(resource='PatientCase', field='id'),
        ]
        dataset = construct_dataset(self.cohort, rules)[0]
        self.assertEqual(self.case.date_of_birth, dataset.get('dateOfBirth'))    
        self.assertEqual(self.case.id, dataset.get('id'))      

    def test_query_date_field(self):
        rule = DatasetRule(resource='PatientCase', field='dateOfBirth')
        dataset = construct_dataset(self.cohort, [rule])[0]
        self.assertEqual(self.case.date_of_birth, dataset.get('dateOfBirth'))       
        
    def test_query_annotated_property(self):
        rule = DatasetRule(resource='PatientCase', field='age')
        dataset = construct_dataset(self.cohort, [rule])[0]
        self.assertEqual(self.case.age, dataset.get('age'))     

    def test_query_coded_concept_text(self):
        rule = DatasetRule(resource='PatientCase', field='gender', transform='GetCodedConceptDisplay')
        dataset = construct_dataset(self.cohort, [rule])[0]
        self.assertEqual(self.case.gender.display, dataset.get('gender.text'))     

    def test_query_coded_concept_code(self):
        rule = DatasetRule(resource='PatientCase', field='gender', transform='GetCodedConceptCode')
        dataset = construct_dataset(self.cohort, [rule])[0]
        self.assertEqual(self.case.gender.code, dataset.get('gender.code'))     

    def test_query_coded_concept_system(self):
        rule = DatasetRule(resource='PatientCase', field='gender', transform='GetCodedConceptSystem')
        dataset = construct_dataset(self.cohort, [rule])[0]
        self.assertEqual(self.case.gender.system, dataset.get('gender.system'))     
        
    def test_case_pseudoidentifier_always_contained(self):
        rule = DatasetRule(resource='PatientCase', field='id')
        dataset = construct_dataset(self.cohort, [rule])[0]
        self.assertIn('pseudoidentifier', dataset)
        self.assertEqual(self.case.pseudoidentifier, dataset.get('pseudoidentifier'))

        
    def test_nested_resources(self):
        therapy = factories.SystemicTherapyFactory.create(case=self.case)
        medication1 = factories.SystemicTherapyMedicationFactory.create(systemic_therapy=therapy)
        medication2 = factories.SystemicTherapyMedicationFactory.create(systemic_therapy=therapy)
        rules = [
            DatasetRule(resource='SystemicTherapy', field='intent', relatedResource='PatientCase'),
            DatasetRule(resource='SystemicTherapyMedication', field='drug', relatedResource='SystemicTherapy', transform='GetCodedConceptDisplay'),
        ]
        dataset = construct_dataset(self.cohort, rules)[0]
        self.assertIn('systemicTherapies', dataset)
        self.assertIn('medications', dataset['systemicTherapies'][0])
        self.assertEqual(therapy.intent, dataset['systemicTherapies'][0]['intent'])
        drugs = [d['drug.text'] for d in dataset['systemicTherapies'][0]['medications']]
        self.assertIn(medication1.drug.display, drugs)
        self.assertIn(medication2.drug.display, drugs)


    def test_nested_resources_without_intermediate(self):
        therapy = factories.SystemicTherapyFactory.create(case=self.case)
        medication1 = factories.SystemicTherapyMedicationFactory.create(systemic_therapy=therapy)
        medication2 = factories.SystemicTherapyMedicationFactory.create(systemic_therapy=therapy)
        rules = [
            DatasetRule(resource='SystemicTherapyMedication', field='drug', relatedResource='SystemicTherapy', transform='GetCodedConceptDisplay'),
        ]
        dataset = construct_dataset(self.cohort, rules)[0]
        self.assertIn('systemicTherapies', dataset)
        self.assertIn('medications', dataset['systemicTherapies'][0])
        self.assertEqual(therapy.intent, dataset['systemicTherapies'][0]['intent'])
        drugs = [d['drug.text'] for d in dataset['systemicTherapies'][0]['medications']]
        self.assertIn(medication1.drug.display, drugs)
        self.assertIn(medication2.drug.display, drugs)

    def test_raises_error_non_existing_schema(self):
        with self.assertRaises(ValidationError):
            rule = DatasetRule(resource='DoesNotExist', field='id')
            construct_dataset(self.cohort, [rule])

    def test_raises_error_non_existing_field(self):
        with self.assertRaises(DatasetRuleProcessingError):
            rule = DatasetRule(resource='PatientCase', field='doesNotExist')
            construct_dataset(self.cohort, [rule])
            
            
class TestAggregationNode(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.node = AggregationNode(
            key='test',
            annotation_nodes=[
                AnnotationNode(key='key1', expression=F('key1')),
                AnnotationNode(key='key2', expression=F('key2')),
            ],
            aggregated_model=MockModel,  
            aggregated_model_parent_related_name='related_name'
        )

    def test_construct_subquery_valid_annotations(self):
        self.node = AggregationNode(
            key='neoplasticEntities',
            annotation_nodes=[
                AnnotationNode(key='id', expression=F('id')),
                AnnotationNode(key='case', expression=F('case')),
            ],
            aggregated_model=models.NeoplasticEntity,  
            aggregated_model_parent_related_name='neoplastic_entities',
        )
        subquery = self.node.aggregated_subquery
        self.assertIsInstance(subquery, ArrayAgg)

    def test_construct_subquery_empty_annotations(self):
        self.node.annotation_nodes = []
        with self.assertRaises(AttributeError):
            self.node.aggregated_subquery

    def test_construct_subquery_missing_aggregated_model(self):
        self.node.aggregated_model = None
        with self.assertRaises(AttributeError):
            self.node.aggregated_subquery

    def test_construct_subquery_missing_aggregated_model_parent_related_name(self):
        self.node.aggregated_model_parent_related_name = None
        with self.assertRaises(AttributeError):
            self.node.aggregated_subquery
            
    def test_annotations_calls_extract_annotations(self):
        node = AggregationNode('key')
        node._extract_annotations = MagicMock()
        node.annotations
        node._extract_annotations.assert_called_once()

    def test_annotations_returns_expected_value(self):
        expected_annotations = {'key1': F('key1'), 'key2': F('key2')}
        self.assertEqual(self.node.annotations, expected_annotations)


class TestDatasetRuleProcessor(TestCase):
    
    def test_basic_rule(self):
        processor = DatasetRuleProcessor(DatasetRule(resource='PatientCase', field='causeOfDeath'))
        self.assertEqual(processor.resource_model, models.PatientCase)
        self.assertEqual(processor.dataset_field, 'causeOfDeath')
        self.assertEqual(processor.model_field_name, 'cause_of_death')
        self.assertEqual(processor.value_transformer, None)
    
    def test_nested_rule(self):
        processor = DatasetRuleProcessor(DatasetRule(resource='NeoplasticEntity', field='relationship', relatedResource='PatientCase'))
        self.assertEqual(processor.resource_model, models.NeoplasticEntity)
        self.assertEqual(processor.parent_model, models.PatientCase)
        self.assertEqual(processor.parent_related_name, 'neoplastic_entities')
        self.assertEqual(processor.dataset_field, 'relationship')
        self.assertEqual(processor.model_field_name, 'relationship')
        self.assertEqual(processor.value_transformer, None)
        
        
        
class TestAnnotationCompiler(TestCase):

    def test_empty_rules(self):
        compiler = AnnotationCompiler([])
        rules = []
        result = compiler._build_aggregation_tree(rules)
        self.assertEqual(result, [])

    def test_build_aggregation_tree_with_single_rule(self):
        compiler = AnnotationCompiler([])
        rule = MagicMock(annotation_key='fieldA', field_annotation=F('fieldA'), resource_model=models.NeoplasticEntity, related_model_lookup='neoplastic_entities')
        result = compiler._build_aggregation_tree([rule])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].key, 'neoplasticEntities')
        self.assertEqual(len(result[0].annotation_nodes), 1)
        self.assertEqual(result[0].annotation_nodes[0].key, 'fieldA')

    def test_build_aggregation_tree_with_multiple_rules_same_resource_model(self):
        compiler = AnnotationCompiler([])
        rule1 = MagicMock(annotation_key='fieldA', field_annotation=F('fieldA'), resource_model=models.NeoplasticEntity, related_model_lookup='neoplastic_entities')
        rule2 = MagicMock(annotation_key='fieldB', field_annotation=F('fieldB'), resource_model=models.NeoplasticEntity, related_model_lookup='neoplastic_entities')
        result = compiler._build_aggregation_tree([rule1, rule2])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].key, 'neoplasticEntities')
        self.assertEqual(len(result[0].annotation_nodes), 2)
        self.assertEqual(result[0].annotation_nodes[0].key, 'fieldA')
        self.assertEqual(result[0].annotation_nodes[1].key, 'fieldB')

    def test_build_aggregation_tree_with_multiple_rules_different_resource_models(self):
        compiler = AnnotationCompiler([])
        rule1 = MagicMock(annotation_key='fieldA', field_annotation=F('fieldA'), resource_model=models.NeoplasticEntity, related_model_lookup='neoplastic_entities')
        rule2 = MagicMock(annotation_key='fieldB', field_annotation=F('fieldB'), resource_model=models.SystemicTherapy, related_model_lookup='systemic_therapies')
        result = compiler._build_aggregation_tree([rule1, rule2])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].key, 'neoplasticEntities')
        self.assertEqual(len(result[0].annotation_nodes), 1)
        self.assertEqual(result[0].annotation_nodes[0].key, 'fieldA')
        self.assertEqual(result[1].key, 'systemicTherapies')
        self.assertEqual(len(result[1].annotation_nodes), 1)
        self.assertEqual(result[1].annotation_nodes[0].key, 'fieldB')

    def test_build_aggregation_tree_with_child_rules(self):
        compiler = AnnotationCompiler([])
        rule1 = MagicMock(annotation_key='fieldA', field_annotation=F('fieldA'), resource_model=models.SystemicTherapy, related_model_lookup='systemic_therapies')
        rule2 = MagicMock(annotation_key='fieldB', field_annotation=F('fieldB'), resource_model=models.SystemicTherapyMedication, related_model_lookup='medications', parent_model=models.SystemicTherapy, parent_relation_lookup='systemic_therapies')
        result = compiler._build_aggregation_tree([rule1, rule2])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].key, 'systemicTherapies')
        self.assertEqual(len(result[0].annotation_nodes), 1)
        self.assertEqual(result[0].annotation_nodes[0].key, 'fieldA')
        self.assertEqual(len(result[0].nested_aggregation_nodes), 1)
        self.assertEqual(result[0].nested_aggregation_nodes[0].key, 'medications')
        self.assertEqual(len(result[0].nested_aggregation_nodes[0].annotation_nodes), 1)
        self.assertEqual(result[0].nested_aggregation_nodes[0].annotation_nodes[0].key, 'fieldB')

    def test_no_aggregation_nodes(self):
        compiler = AnnotationCompiler([])
        annotations, queryset_fields = compiler.generate_annotations()
        self.assertEqual(annotations, {})
        self.assertEqual(queryset_fields, ['pseudoidentifier'])

    def test_aggregation_node_no_key(self):
        compiler = AnnotationCompiler([])
        annotation_node = AnnotationNode(key='test_key', expression=F('test_expression'))
        aggregation_node = AggregationNode(key=None, annotation_nodes=[annotation_node])
        compiler.aggregation_nodes = [aggregation_node]
        annotations, queryset_fields = compiler.generate_annotations()
        self.assertEqual(annotations, {'test_key': F('test_expression')})
        self.assertEqual(queryset_fields, ['pseudoidentifier', 'test_key'])

    def test_aggregation_node_with_key_and_annotations(self):
        compiler = AnnotationCompiler([])
        annotation_node = AnnotationNode(key='test_annotation', expression=F('test_annotation_expression'))
        aggregation_node = AggregationNode(key='test_key', annotation_nodes=[annotation_node], aggregated_model=MagicMock(), aggregated_model_parent_related_name='related_name')
        compiler.aggregation_nodes = [aggregation_node]
        annotations, queryset_fields = compiler.generate_annotations()
        self.assertEqual(queryset_fields, ['pseudoidentifier', 'test_key'])

    def test_multiple_aggregation_nodes(self):
        compiler = AnnotationCompiler([])
        annotation_node1 = AnnotationNode(key='test_annotation1', expression=F('test_expression1'))
        annotation_node2 = AnnotationNode(key='test_annotation2', expression=F('test_expression2'))
        aggregation_node1 = AggregationNode(key=None, annotation_nodes=[annotation_node1], aggregated_model=MagicMock(), aggregated_model_parent_related_name='related_name')
        aggregation_node2 = AggregationNode(key='test_key2', annotation_nodes=[annotation_node2], aggregated_model=MagicMock(), aggregated_model_parent_related_name='related_name')
        compiler.aggregation_nodes = [aggregation_node1, aggregation_node2]
        annotations, queryset_fields = compiler.generate_annotations()
        self.assertEqual(queryset_fields, ['pseudoidentifier', 'test_annotation1', 'test_key2'])

    def test_annotation_node_key_in_DATASET_ROOT_FIELDS(self):
        compiler = AnnotationCompiler([])
        annotation_node = AnnotationNode(key='pseudoidentifier', expression=F('test_expression'))
        aggregation_node = AggregationNode(key=None, annotation_nodes=[annotation_node])
        aggregation_node.annotation_nodes = [annotation_node]
        compiler.aggregation_nodes = [aggregation_node]
        annotations, queryset_fields = compiler.generate_annotations()
        self.assertEqual(annotations, {})
        self.assertEqual(queryset_fields, ['pseudoidentifier'])