from typing import List, Dict, Tuple, Optional,  Union, Set

from django.db.models import Expression, F, Subquery, OuterRef, QuerySet, Model as DjangoModel
from django.db.models.functions import JSONObject
from django.contrib.postgres.aggregates import ArrayAgg

from pop.core import transforms
from pop.core.utils import get_related_model_from_field, to_camel_case

from pop.oncology.models import PatientCase

from pop.analytics.schemas import DatasetRule


DATASET_ROOT_FIELDS = [f.name for f in PatientCase._meta.get_fields()]

class DatasetRuleProcessor:
    """Processes individual dataset rules and extracts necessary query information."""

    def __init__(self, rule: DatasetRule):
        self.dataset_field = rule.field
        self.resource_schema = self._get_schema(rule.resource.value)
        self.resource_model = self.resource_schema.__orm_model__
        self.value_transformer = self._get_transformer(rule.transform)
        self.parent_model: Optional[DjangoModel] = None
        self.parent_relation_lookup: Optional[str] = None

    def _get_schema(self, resource_name: str):
        """Retrieves the corresponding schema for the resource."""
        from pop.oncology import schemas as oncology_schemas
        return getattr(oncology_schemas, f"{resource_name}Schema")

    def _get_transformer(self, transform: Optional[Union[str, tuple]]):
        """Fetches transformation function if specified, otherwise defaults."""
        return getattr(transforms, transform or "", None) or transforms.DEFAULT_TRANSFORMATIONS.get(self.field_data_type)

    @property
    def annotation_key(self) -> str:
        """Returns a unique key used in dataset query annotations."""
        return f"{self.dataset_field}.{self.value_transformer.name}" if self.value_transformer else self.dataset_field

    @property
    def related_model_lookup(self) -> str:
        """Determines the Django ORM lookup for related models."""
        if self.resource_model._meta.model_name == "patientcase":
            return ""  # No relation needed for PatientCase
        if self.parent_model:
            return {field.related_model: field.name for field in self.parent_model._meta.get_fields()}[self.resource_model]
        return self.resource_model._meta.get_field("case").related_query_name()

    @property
    def schema_field_info(self):
        """Retrieves metadata about the dataset field from the schema."""
        return self.resource_schema.model_fields.get(self.dataset_field)

    @property
    def field_data_type(self):
        """Determines the data type of the field in the schema."""
        return get_related_model_from_field(self.schema_field_info) or self.schema_field_info.annotation

    @property
    def resource_model_field(self):
        """Gets the Django model field corresponding to the schema alias."""
        return self.resource_model._meta.get_field(self.schema_field_info.alias)

    @property
    def query_lookup_path(self) -> str:
        """Generates the Django ORM lookup path for querying the dataset field."""
        return f"{self.related_model_lookup}__{self.resource_model_field.name}" if self.related_model_lookup else self.resource_model_field.name

    @property
    def field_annotation(self):
        """Returns the Django ORM annotation for this dataset field."""
        return self.value_transformer.generate_annotation_expression(self.query_lookup_path) if self.value_transformer else F(self.query_lookup_path)
from dataclasses import dataclass, field
from typing import Dict, List, Any



@dataclass
class AnnotationNode:
    """
    Represents an annotation node with a key and an associated expression.

    Attributes:
        key (str): The unique identifier for the annotation.
        expression (Expression): The Django ORM expression associated with the annotation.
    """
    key: str
    expression: Expression




@dataclass
class AggregationNode:
    """
    Represents an aggregation node with a key and an associated list of
    annotation nodes and/or nested aggregation nodes.

    Attributes:
        key (str): The unique identifier for the aggregation.
        annotation_nodes (List[AnnotationNode]): The annotations associated with
            the aggregation.
        nested_aggregation_nodes (List[AggregationNode]): The nested aggregations
            associated with the aggregation.
        aggregated_model (DjangoModel): The Django model that the aggregation
            operates on.
        aggregations_model_related_name (str): The related name of the model that
            the aggregation operates on.
    """
    key: str
    annotation_nodes: List[AnnotationNode] = field(default_factory=list)
    nested_aggregation_nodes: List["AggregationNode"] = field(default_factory=list)
    aggregated_model: DjangoModel = None 
    aggregations_model_related_name: str = None

    @property
    def annotations(self) -> Dict[str, Expression]:
        """
        Returns a dictionary of annotations for the aggregation.

        The returned dictionary contains the keys of the annotations as specified
        in the annotation nodes and the values are the corresponding Django ORM
        expressions.

        If the aggregation node has nested aggregation nodes, their annotations
        are also included in the returned dictionary.
        """
        return self._extract_annotations()

    @property
    def aggregated_subquery(self) -> Subquery:
        """
        Returns a subquery that can be used to create a Django ORM expression
        which will annotate a queryset with the aggregated results of the
        annotation nodes.

        The returned subquery aggregates the annotations of the annotation nodes
        and returns a single value of type JSONB which contains the aggregated
        results.

        The subquery is constructed by annotating the aggregated model with a
        JSONB object that contains the aggregated results of the annotation nodes.
        The subquery is then filtered to only include the related objects
        specified by the aggregations_model_related_name.

        The subquery is annotated with a single field named `related_json_object`
        which contains the JSONB object with the aggregated results.

        If the aggregation node has nested aggregation nodes, their annotations
        are also included in the returned JSONB object.

        Raises:
            AttributeError: If the aggregation node's subquery cannot be
                constructed without an aggregated model and its related name.
            AttributeError: If the aggregation node's subquery cannot be
                constructed without annotations.
        """
        if not self.aggregated_model or not self.aggregations_model_related_name:
            raise AttributeError("The aggregation node's subquery cannot be constructed without an aggregated model and its related name.")
        annotations = self.annotations
        if not annotations:
            raise AttributeError("The aggregation node's subquery cannot be constructed without annotations.")
        return Subquery(
            self.aggregated_model.objects.filter(
                id=OuterRef(f'{self.aggregations_model_related_name}__id')
            ).annotate(
                related_json_object=ArrayAgg(JSONObject(**annotations), distinct=True)
            ).values('related_json_object')[:1]
        )

    def add_annotation_node(self, key: str, expression: Expression) -> None:
        """
        Adds an annotation node to the current aggregation node.

        The annotation node is constructed from the given key and expression.

        The added annotation node is included in the annotations of the
        current aggregation node.

        Args:
            key: The key to use for the annotation node.
            expression: The expression to use for the annotation node.

        Returns:
            None
        """
        self.annotation_nodes.append(AnnotationNode(key, expression))

    def add_nested_aggregation_node(self, node: "AggregationNode") -> None:
        """
        Adds a nested aggregation node to the current aggregation node.

        The added nested aggregation node is included in the annotations of the
        current aggregation node.

        Args:
            node: The nested aggregation node to add.

        Returns:
            None
        """
        self.nested_aggregation_nodes.append(node)

    def _extract_annotations(self) -> Dict:
        """
        Extracts the annotations for the current aggregation node.

        The returned dictionary contains the annotations in one of three forms.

        Case 1: PatientCase properties at root of dataset. The key is the name
        of the property and the value is the Django ORM expression for the
        property.

        Case 2: Nested resources. The key is the name of the nested resource and
        the value is the subquery for the nested resource.

        Case 3: Simple annotations. The key is the name of the annotation and the
        value is the Django ORM expression for the annotation.

        Returns:
            Dict[str, Expression]: A dictionary of annotations.
        """
        annotations = {}
        # Case 2: Nested resources
        for nested_node in self.nested_aggregation_nodes:
            annotations[nested_node.key] = nested_node.aggregated_subquery
        # Case 3: Simple annotations
        for annotation_node in self.annotation_nodes:
            annotations[annotation_node.key] = annotation_node.expression
        return annotations


class AnnotationCompiler:
    """
    Compiles a list of dataset rules into an aggregation tree and
    generates the corresponding Django ORM annotations.

    The tree is built by grouping rules by their resource models and
    creating an AggregationNode for each group. Annotation nodes are then
    added to the corresponding AggregationNode. The tree is built
    recursively by processing child rules for each node.
    """

    def __init__(self, rules: List[DatasetRule]):
        """
        Initializes the AnnotationCompiler with a list of dataset rules.

        Args:
            rules: A list of dataset rules
        """
        self.rules = [DatasetRuleProcessor(rule) for rule in rules]
        self._resolve_rule_resource_relations()
        self.aggregation_nodes: List[AggregationNode] = self._build_aggregation_tree(self.rules)

    def generate_annotations(self) -> Tuple[Dict[str, Expression], List[str]]:
        """
        Generates the Django ORM annotations for the dataset.

        The annotations are generated by traversing the aggregation tree
        and building a dictionary of annotations. The dictionary contains
        the annotations in one of three forms.

        Case 1: PatientCase properties at root of dataset. The key is the name
        of the property and the value is the Django ORM expression for the
        property.

        Case 2: Nested resources. The key is the name of the nested resource and
        the value is the subquery for the nested resource.

        Case 3: Simple annotations. The key is the name of the annotation and the
        value is the Django ORM expression for the annotation.

        Args:
            None

        Returns:
            A tuple of two elements. The first element is a dictionary of
            annotations and the second element is a list of field names.
        """
        annotations = {}
        queryset_fields = ['pseudoidentifier'] 
        for aggregation_node in self.aggregation_nodes:    
            # Case 1: PatientCase properties at root of dataset
            if not aggregation_node.key: 
                for annotation_node in aggregation_node.annotation_nodes:
                    if annotation_node.key not in DATASET_ROOT_FIELDS:
                        annotations[annotation_node.key] = annotation_node.expression
                    if annotation_node.key not in queryset_fields:
                        queryset_fields.append(annotation_node.key)                                
            elif aggregation_node.annotations:
                annotations[aggregation_node.key] = ArrayAgg(JSONObject(**aggregation_node.annotations), distinct=True)
                queryset_fields.append(aggregation_node.key)      
        # Remove duplicates 
        return annotations, queryset_fields
    
    def _resolve_rule_resource_relations(self) -> None:
        """
        Resolves the resource relations between rules.

        The method creates a dictionary that maps each resource schema to
        its corresponding rule. The dictionary is then used to resolve the
        parent model and related lookup for each rule.
        """
        schema_to_rule = {rule.resource_schema: rule for rule in self.rules}
        for rule in self.rules:
            if rule.resource_schema in schema_to_rule:
                parent_rule = schema_to_rule[rule.resource_schema]
                rule.parent_model = parent_rule.resource_model
                rule.parent_relation_lookup = parent_rule.related_model_lookup

    def _build_aggregation_tree(self, rules: List[DatasetRuleProcessor], parent_node: Optional[AggregationNode] = None, assigned_rules: Set[DatasetRuleProcessor] = None) -> List[AggregationNode]:
        """
        Recursively builds an aggregation tree from a list of dataset rules.

        The tree is built by grouping rules by their resource models and
        creating an AggregationNode for each group. Annotation nodes are then
        added to the corresponding AggregationNode. The tree is built
        recursively by processing child rules for each node.

        Args:
            rules: A list of dataset rules
            parent_node: The parent node of the current node
            assigned_rules: A set of rules that have already been processed

        Returns:
            A list of root nodes in the aggregation tree
        """
        node_map = {}  
        if assigned_rules is None:
            assigned_rules = set()
        for rule in rules:
            if rule in assigned_rules:
                continue
            else:
                assigned_rules.add(rule)
            resource_key = to_camel_case(rule.related_model_lookup or rule.parent_relation_lookup)
            if resource_key not in node_map:
                node = AggregationNode(
                    key=resource_key,
                    aggregated_model=rule.resource_model,
                    aggregations_model_related_name=rule.parent_relation_lookup
                )
                node_map[resource_key] = node
            node = node_map[resource_key]
            # Add annotation nodes to the corresponding AggregationNode
            node.add_annotation_node(rule.annotation_key, rule.field_annotation)
            # Recursively build the tree for child rules
            child_rules = [r for r in rules if r.parent_relation_lookup == rule.related_model_lookup]
            if child_rules:
                child_node = self._build_aggregation_tree(child_rules, node, assigned_rules)
                node.nested_aggregation_nodes.extend(child_node)
        # Return the root nodes (i.e., nodes with no parent)
        root_nodes = [node for node in node_map.values() if parent_node is None or node.key != parent_node.key]
        return root_nodes



class QueryCompiler:
    """Compiles a dataset query based on user-defined rules

    QueryCompiler takes a cohort and a set of rules as input, and returns
    a QuerySet representing the dataset for that cohort.

    Attributes:
        cohort (pop.analytics.models.Cohort): The cohort to generate the
            dataset for
        rules (List[DatasetRule]): The user-defined rules for generating the
            dataset
    """

    def __init__(self, cohort, rules: List[DatasetRule]):
        self.cohort = cohort
        self.rule_compiler = AnnotationCompiler(rules)

    def compile(self) -> QuerySet:
        """
        Compiles a QuerySet based on the rules provided

        Returns:
            QuerySet: The dataset for the cohort
        """
        annotations, queryset_fields = self.rule_compiler.generate_annotations()
        print(annotations, queryset_fields)
        return self.cohort.cases.annotate(**annotations).values(*queryset_fields)
    
def construct_dataset(cohort, rules: List[DatasetRule]) -> QuerySet:
    """
    Compiles a QuerySet based on the rules provided

    Args:
        cohort (pop.analytics.models.Cohort): The cohort to generate the
            dataset for
        rules (List[DatasetRule]): The user-defined rules for generating the
            dataset

    Returns:
        QuerySet: The dataset for the cohort
    """
    return QueryCompiler(cohort, rules).compile()
