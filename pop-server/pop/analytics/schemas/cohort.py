

from typing import Optional, Tuple, Any, List, Union, Iterator
from pydantic import AliasChoices
from enum import Enum

from django.db.models import Q, Exists, OuterRef
from ninja import Schema, Field

from pop.analytics import models as orm
from pop.oncology import models as oncology_models
from pop.core.serialization import filters as filters_module
from pop.core.utils import camel_to_snake
from pop.core.serialization.factory import create_filters_schema
from pop.core.serialization.metaclasses import ModelGetSchema, ModelCreateSchema, SchemaConfig


# ----------------------------------------------------
# Cohort definition schemas
# ----------------------------------------------------

class RulesetCondition(str, Enum):
    AND = 'and'
    OR = 'or'

CohortQueryEntity = Enum('CohortQueryEntity', {
    model.__name__: model.__name__ for model in oncology_models.MODELS
}, type=str)

CohortQueryFilter = Enum('CohortQueryFilter', {
    filter.__name__: filter.__name__ for filter in filters_module.__all__
}, type=str)

class CohortRuleFilter(Schema):
    field: str = Field(
        title='Field', 
        description="Dot-separated path of the resource field (e.g. 'medications.drug')", 
    )
    operator: CohortQueryFilter = Field( # type: ignore
        title='Operator', 
        description="Name of the filter operator to be applied to the field", 
    )
    value: Any  = Field(
        title='Value', 
        description="Filter value to be applied to the field using the rule's oprerator", 
    )    
    
    @property
    def db_field(self):
        return '__'.join([camel_to_snake(step) for step in self.field.split('.')])
    

class CohortRule(Schema):
    entity: CohortQueryEntity = Field( # type: ignore
        title='entity', 
        description="Name of the case-related resource", 
    )
    filters: List[CohortRuleFilter] = Field(
        title='Filters', 
        description="List of filters to be applied to the resource",
    )

    def convert_to_query(self) -> Iterator[Q]:
        model = getattr(oncology_models, self.entity, None)
        subquery = Q()
        for filter in self.filters:
            operator = getattr(filters_module, filter.operator, None)
            field = filter.db_field
            subquery = subquery & operator.get_query(field, filter.value, model)

        if model is oncology_models.PatientCase:
            yield subquery
        else:
            subquery = model.objects.filter(Q(case=OuterRef("pk")) & subquery)
            yield Q(Exists(subquery))

class CohortRuleset(Schema):
    condition: RulesetCondition = Field(
        default=RulesetCondition.AND,
        title='Logical condition', 
        description='Logical condition used to chain the rules within the ruleset', 
    )
    rules: List[Union[CohortRule, 'CohortRuleset']] = Field(
        title='Rules', 
        description='List of rules or nested rulesets that define the fields and values to use for the filtering.', 
    )
    
    def convert_to_query(self) -> Iterator[Q]:
        query = Q()
        for rule in self.rules:
            for rule_query in rule.convert_to_query():
                if self.condition == RulesetCondition.AND:
                    query = rule_query & query
                if self.condition == RulesetCondition.OR:
                    query = rule_query | query
        # Yield the completed, compiled logic for this branch of query back up the pipe:
        yield query


# ----------------------------------------------------
# Cohort model schemas
# ----------------------------------------------------

class CohortSchema(ModelGetSchema):
    population: int = Field(
        title='Population', 
        description='Cohort population', 
        alias='db_population', 
        validation_alias=AliasChoices('db_population','population')
    )
    config = SchemaConfig(model=orm.Cohort)

class CohortCreateSchema(ModelCreateSchema):
    includeCriteria: Optional[CohortRuleset] = Field(
        default=None,
        title='Inclusion critera', 
        description='Logic rules to filter and constrain the cases to be included in the cohort', 
        alias='include_criteria', 
        validation_alias=AliasChoices('includeCriteria','include_criteria')
    )
    excludeCriteria: Optional[CohortRuleset] = Field(
        default=None,
        title='Exclusion critera', 
        description='Logic rules to filter and constrain the cases to be excluded from the cohort', 
        alias='exclude_criteria', 
        validation_alias=AliasChoices('excludeCriteria','exclude_criteria')
    )
    config = SchemaConfig(model=orm.Cohort)

class CohortFilters(create_filters_schema(schema=CohortSchema, name='CohortFilters')):
    createdBy: Optional[str] = Field(None, description='Filter for a particular cohort creator by its username')

    def filter_createdBy(self, value: str) -> Q:
        return Q(created_by=self.createdBy) if value is not None else Q()

# ----------------------------------------------------
# Cohort traits schemas
# ----------------------------------------------------

class CohortTraitAverage(Schema):
    average: float
    standardDeviation: Optional[float]

class CohortTraitMedian(Schema):
    median: float
    interQuartalRange: Tuple[float, float]

class CohortTraitCounts(Schema):
    category: str
    counts: int
    percentage: float

class CohortContribution(Schema):
    contributor: str
    contributions: int
