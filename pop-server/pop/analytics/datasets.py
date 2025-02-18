from  typing import Optional, List
from django.db.models import F 
from django.db.models.functions import JSONObject
from django.contrib.postgres.aggregates import ArrayAgg
from pop.analytics.schemas.datasets import DatasetDefinitionRule, DataResource
from pop.analytics.models.cohort import Cohort
from pop.core.utils import to_camel_case
from collections import defaultdict
from django.db.models import F, Subquery, OuterRef
from pop.oncology import models as oncology_models
from pop.oncology import schemas as oncology_schemas
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.utils import get_related_model_from_field

class DatasetDefinitionRule(DatasetDefinitionRule):
    
    parent: Optional["DatasetDefinitionRule"] = None
    
    @property
    def resource_schema(self):
        return getattr(oncology_schemas, f'{self.resource.value}Schema')
    
    @property
    def resource_orm_model(self):
        return self.resource_schema.__orm_model__
    
    @property 
    def resource_orm_related_name(self):
        if self.resource_orm_model is oncology_models.PatientCase:
            return ''
        else:
            if self.parent:
                return {field.related_model: field.name for field in self.parent.resource_orm_model._meta.get_fields()}[self.resource_orm_model]
            else:
                return self.resource_orm_model._meta.get_field('case')._related_name

    @property 
    def schema_field(self):
        return self.resource_schema.model_fields.get(self.field)
    
    @property 
    def orm_field(self):
        return self.resource_orm_model._meta.get_field(self.schema_field.alias)

    @property 
    def child_resources(self):
        return [
            get_related_model_from_field(field).__name__ for field in self.resource_schema.model_fields.values() if get_related_model_from_field(field) and issubclass(get_related_model_from_field(field), ModelGetSchema) 
        ]
        
    @property
    def related_orm_lookup(self):
        return f'{self.resource_orm_related_name}__{self.orm_field.name}'

    @property 
    def annotation(self):
        return F(self.related_orm_lookup)

    @property 
    def annotation(self):
        return F(self.related_orm_lookup)

def construct_subquery(parent_rule, annotations):
    return Subquery(
        parent_rule.resource_orm_model.objects.filter(
            id=OuterRef(f'{parent_rule.resource_orm_related_name}__id')
        ).annotate(
            related_json_object=ArrayAgg(JSONObject(**annotations), distinct=True)
        ).values('related_json_object')[:1]  # Ensures a single JSON array for medications
    )

def build_rule_tree(rules):
    """Builds a tree-like dictionary from dataset definition rules."""
    
    tree = defaultdict(dict)
    children_map = defaultdict(list)
    
    # Step 1: Organize rules by parent
    for rule in rules:
        if rule.parent:
            children_map[to_camel_case(rule.parent.resource_orm_related_name)].append(rule)        
        else:
            tree[to_camel_case(rule.resource_orm_related_name)][to_camel_case(rule.field)] = rule
    
    # Step 2: Recursively attach children
    def attach_children(parent_name):
        if parent_name in children_map:
            for child in children_map[parent_name]:
                child_name = to_camel_case(child.resource_orm_related_name)
                if child_name not in tree[parent_name]:
                    tree[parent_name][child_name] = {}
                tree[parent_name][child_name][to_camel_case(child.field)] = child
                attach_children(child_name)  # Recursively process child nodes

    # Process root-level nodes
    for parent_name in list(tree.keys()):
        attach_children(parent_name)
    return tree

def construct_dataset(cohort: Cohort,  rules: List[DatasetDefinitionRule]):

    # Step 2: Build parent-child relationships
    for rule in rules:
        for parent in rules:
            if rule.resource in parent.child_resources:
                rule.parent = parent
                
    from pprint import pprint 
    # Usage
    tree = build_rule_tree(rules)

    def process_rules_recursively(rules):
        annotations = {}
        for label, rule in rules.items():
            if isinstance(rule, dict):
                annotations[label] = construct_subquery(list(rule.values())[0].parent, process_rules_recursively(rule))
            else:
                annotations[label] = rule.annotation
        return annotations
            

    annotations = defaultdict()
    case_properties = tree.pop('', {}) 
    for label, rules in tree.items():    
        annotations[label] = ArrayAgg(JSONObject(**process_rules_recursively(rules)), distinct=True)
    dataset = cohort.annotate(**annotations).values('pseudoidentifier',*list(case_properties.keys()), *list(tree.keys()))
    pprint(dataset)
    return dataset