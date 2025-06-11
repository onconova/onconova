from typing import List, Dict, Tuple, Optional,  Union, Set
import inspect 
from django.db.models import Expression, F, Subquery, OuterRef, QuerySet, Model as DjangoModel, Exists, Value
from django.db.models.functions import JSONObject
from django.contrib.postgres.aggregates import ArrayAgg, JSONBAgg

from queryable_properties.properties.base import QueryablePropertyDescriptor

from pop.core.utils import get_related_model_from_field, to_camel_case
from pop.core.models import BaseModel

from dataclasses import dataclass, field
from typing import Dict, List, Any

from pop.oncology.models import PatientCase, MODELS
from pop.analytics.schemas import DatasetRule

class DatasetRuleProcessingError(RuntimeError): pass

DATASET_ROOT_FIELDS = [f.name for f in PatientCase._meta.get_fields()]

class DatasetRuleProcessor:
    """Processes individual dataset rules and extracts necessary query information."""
    
    def __init__(self, rule: DatasetRule):
        self.schema_field = rule.field
        # Get the schema specified by the rule 
        schema = self._get_schema(rule.resource.value)
        self.resource_model = self._get_orm_model(schema)
        # Resolve the related 
        if self.resource_model == PatientCase:
            self.parent_model = None
        elif hasattr(self.resource_model, 'case'):
            self.parent_model = PatientCase
        else:
            self.parent_model = next((
                field.related_model for field in self.resource_model._meta.get_fields() 
                    if field.related_model and hasattr(field.related_model,'case')
            ))                               
        # Get other values
        self.model_field_name = self._get_model_field_name(schema)
        self.model_field = self._get_model_field(self.resource_model, self.model_field_name)
        self.value_transformer = self._get_transformer(rule.transform)
    
        
    def _get_schema(self, resource_name: str):
        """Retrieves the corresponding schema for the resource."""
        from pop.oncology import schemas as oncology_schemas
        schema = getattr(oncology_schemas, f"{resource_name}Schema", None)
        if not schema:
            raise DatasetRuleProcessingError(f'Could not resolve schema "{resource_name}" into an existing class object.')
        return schema
    
    def _get_model_field(self, orm_model, field_name: str):
        """Retrieves the corresponding schema for the resource."""
        try:
            return orm_model._meta.get_field(field_name)
        except:
            return getattr(orm_model, field_name)
    
    def _get_orm_model(self, schema):
        """Retrieves the corresponding schema for the resource."""
        orm_model = schema.get_orm_model()
        if not orm_model:
            raise DatasetRuleProcessingError(f'The schema "{schema.__name__}" has no associated ORM model.')
        return orm_model
    
    def _get_model_field_name(self, schema):
        """Retrieves the corresponding schema for the resource."""
        schema_field_info = schema.model_fields.get(self.schema_field)        
        if not schema_field_info:
            raise DatasetRuleProcessingError(f'Could not resolve field "{self.schema_field}" into a schema or ORM model field.')
        return schema_field_info.alias or self.schema_field

    def _get_transformer(self, transform: Optional[Union[str, tuple]]):
        """Fetches transformation function if specified, otherwise defaults."""
        if not transform:
            return None
        from pop.core.serialization import transforms
        transform_class = getattr(transforms, transform or "", None)
        if not transform_class:
            raise DatasetRuleProcessingError(f'Could not resolve transform "{transform}" into a transform class object.')
        return transform_class

    @property
    def annotation_key(self) -> str:
        """Returns a unique key used in dataset query annotations."""
        return f"{self.model_field_name}.{self.value_transformer.name}" if self.value_transformer else self.model_field_name

    @property 
    def parent_related_name(self):
        return next((field.name for field in self.parent_model._meta.get_fields() if inspect.isclass(field.related_model) and issubclass(self.resource_model, field.related_model))) if self.parent_model else None

    @property
    def related_model_annotation_key(self) -> str:
        """Determines the Django ORM lookup for related models."""
        if self.resource_model._meta.model_name.lower() == "patientcase":
            return ""  
        if self.parent_model:
            if not self.resource_model.__bases__[0] == BaseModel:
                return self.resource_model._meta.verbose_name_plural.replace(' ','_')
            else:
                return self.parent_related_name 
        else:
            key = self.resource_model._meta.get_field("case").related_query_name()
            return f'{key}'
        
    @property
    def query_lookup_path(self) -> str:
        """Generates the Django ORM lookup path for querying the dataset field."""
        return self.model_field_name

    @property
    def field_annotation(self):
        """Returns the Django ORM annotation for this dataset field."""
        if self.model_field_name == 'clinical_identifier':
            query_expression = Value('***********')
        elif self.value_transformer:
            query_expression = self.value_transformer.generate_annotation_expression(self.query_lookup_path)
        else: 
            query_expression = F(self.query_lookup_path)
        if getattr(self.model_field, 'is_relation', None) and (self.model_field.one_to_many or self.model_field.many_to_many):
            return ArrayAgg(query_expression, distinct=True)
        else:
            return query_expression


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
    aggregated_model_parent_related_name: str = None

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
    def subquery(self) -> Subquery: 
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

        if not self.aggregated_model or not self.aggregated_model_parent_related_name:
            raise AttributeError("The aggregation node's subquery cannot be constructed without an aggregated model and its related name.")
        annotations = self.annotations
        if 'Id' not in annotations:
            annotations.update({'Id': F('id')})
        if not annotations:
            raise AttributeError("The aggregation node's subquery cannot be constructed without annotations.")
        return Subquery(
            self.aggregated_model.objects.filter(
                id=OuterRef(f'{self.aggregated_model_parent_related_name}__id'),
            ).annotate(
                related_json_object=JSONObject(**annotations)
            ).filter(related_json_object__isnull=False).values('related_json_object')[:1]
        )
        
    @property
    def aggregated_subquery(self) -> ArrayAgg:
        return ArrayAgg(self.subquery, distinct=True, filter=Exists(self.subquery))

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
                aggregation_node.key = aggregation_node.key + '_resources'
                annotations[aggregation_node.key] = aggregation_node.aggregated_subquery                    
                queryset_fields.append(aggregation_node.key)      
        # Remove duplicates 
        return annotations, queryset_fields
    
    def _generate_node_map(self, rules):
        from collections import defaultdict
        node_map = defaultdict(dict)            
        for rule in rules:
            if rule.parent_model not in node_map or rule.resource_model not in node_map[rule.parent_model]:
                node = AggregationNode(
                    key=rule.related_model_annotation_key or '',
                    aggregated_model=rule.resource_model,
                    aggregated_model_parent_related_name=rule.parent_related_name
                )
                node_map[rule.parent_model][rule.resource_model] = node
            node = node_map[rule.parent_model][rule.resource_model]
            # Add annotation nodes to the corresponding AggregationNode
            node.add_annotation_node(rule.annotation_key, rule.field_annotation)
        
        for rule in rules:
            if rule.parent_model:
                grandparent_model = PatientCase
                grandparent_related_field = {field.related_model: field for field in grandparent_model._meta.get_fields()}.get(rule.parent_model)                
                if grandparent_related_field and rule.parent_model not in node_map[grandparent_model]:
                    node = AggregationNode(
                        key=grandparent_related_field.name or '',
                        aggregated_model=rule.parent_model,
                        aggregated_model_parent_related_name=grandparent_related_field.name
                    )
                    node.add_annotation_node('id', F('id'))       
                    node_map[grandparent_model][rule.parent_model] = node
        return node_map

    def _build_aggregation_tree(self, rules):
        self.nodes_map = self._generate_node_map(rules)
        return self._build_tree(None) + self._build_tree(PatientCase)

    def _build_tree(self, parent) -> List[AggregationNode]:
        nodes = []
        for node in self.nodes_map[parent].values():
            child_nodes = self._build_tree(node.aggregated_model)
            node.nested_aggregation_nodes.extend(child_nodes)
            nodes.append(node)
        return nodes 


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
