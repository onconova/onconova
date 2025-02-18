from  typing import Optional, List
from django.db.models import F 
from django.db.models.functions import JSONObject
from django.contrib.postgres.aggregates import ArrayAgg
from pop.analytics.schemas import DatasetRule, DataResource
from pop.analytics.models.cohort import Cohort
from pop.core.utils import to_camel_case
from collections import defaultdict
from django.db.models import F, Subquery, OuterRef
from pop.oncology.models import PatientCase

def build_rule_tree(rules):   
    tree = defaultdict(dict)
    children_map = defaultdict(list)
    
    # Step 1: Organize rules by parent
    for rule in rules:
        if rule._parent:
            children_map[to_camel_case(rule._parent.resource_orm_related_name)].append(rule)        
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

def construct_subquery(parent_rule, annotations):
    """
    Construct a subquery for the related resource with aggregated JSON fields.
    
    Args:
        parent_rule: The parent DatasetDefinitionRule defining the relationship.
        annotations: The annotations to be included in the subquery.
    
    Returns:
        A Django Subquery to fetch the related data.
    """
    return Subquery(
        parent_rule.resource_orm_model.objects.filter(
            id=OuterRef(f'{parent_rule.resource_orm_related_name}__id')
        ).annotate(
            related_json_object=ArrayAgg(JSONObject(**annotations), distinct=True)
        ).values('related_json_object')[:1]  # Ensures a single JSON array for medications
    )


def construct_dataset(cohort: Cohort,  rules: List[DatasetRule]):
    """
    Constructs the dataset for a cohort based on rules and returns the dataset.
    
    Args:
        cohort: The cohort to apply the rules on.
        rules: List of DatasetRule to process and build the dataset.
    
    Returns:
        The constructed dataset with applied annotations.
    """
    for rule in rules:
        for parent in rules:
            if rule.resource in parent.child_resources:
                rule._parent = parent
                
    # Build tree from the dataset definition rules
    tree = build_rule_tree(rules)

    def process_rules_recursively(rules):
        annotations = {}
        for label, rule in rules.items():
            if isinstance(rule, dict):
                annotations[label] = construct_subquery(list(rule.values())[0]._parent, process_rules_recursively(rule))
            else:
                annotations[label] = rule.annotation
        return annotations

    # Create the annotations and dataset from the tree
    annotations = defaultdict()
    case_properties = tree.pop('', {}) 
    annotations = {
       label: rule.annotation for label, rule in case_properties.items() if label not in [f.name for f in PatientCase._meta.get_fields()]
    }
    for label, rules in tree.items():    
        annotations[label] = ArrayAgg(JSONObject(**process_rules_recursively(rules)), distinct=True)
    
    # Query the database to export the dataset
    dataset = list(cohort.cases.annotate(**annotations).values(
        'pseudoidentifier',
        *list(case_properties.keys()), 
        *list(tree.keys())
    ))
    print([rule.orm_field.name for rule in case_properties.values()])
    return dataset