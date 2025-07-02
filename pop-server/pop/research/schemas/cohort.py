from typing import Optional, Tuple, Any, List, Union, Iterator
from pydantic import AliasChoices
from enum import Enum

from django.db.models import Q, Exists, OuterRef
from ninja import Schema, Field

from pop.research.models import cohort as orm
from pop.oncology import models as oncology_models
from pop.core.serialization import filters as filters_module
from pop.core.utils import camel_to_snake
from pop.core.serialization.factory import create_filters_schema
from pop.core.serialization.metaclasses import (
    ModelGetSchema,
    ModelCreateSchema,
    SchemaConfig,
)


class RulesetCondition(str, Enum):
    """Logical connector for combining multiple cohort rules."""

    AND = "and"
    OR = "or"


# Dynamically create an Enum from oncology model class names
CohortQueryEntity = Enum(
    "CohortQueryEntity",
    {model.__name__: model.__name__ for model in oncology_models.MODELS},
    type=str,
)

# Dynamically create an Enum from available filter class names
CohortQueryFilter = Enum(
    "CohortQueryFilter",
    {filter.__name__: filter.__name__ for filter in filters_module.__all__},
    type=str,
)


class CohortRuleFilter(Schema):
    """
    Represents a single filter within a cohort rule, applied to a model field.
    """

    field: str = Field(
        title="Field",
        description="Dot-separated path of the resource field (e.g. 'medications.drug')",
    )
    operator: CohortQueryFilter = Field(  # type: ignore
        title="Operator",
        description="Name of the filter operator to be applied to the field",
    )
    value: Any = Field(
        title="Value",
        description="Filter value to be applied to the field using the rule's oprerator",
    )

    @property
    def db_field(self):
        """
        Converts a dot-separated field path into Django ORM double-underscore syntax.
        """
        return "__".join([camel_to_snake(step) for step in self.field.split(".")])


class CohortRule(Schema):
    """
    Represents a set of filters applied to a specific entity (model/table).
    """

    entity: CohortQueryEntity = Field(  # type: ignore
        title="entity",
        description="Name of the case-related resource",
    )
    filters: List[CohortRuleFilter] = Field(
        title="Filters",
        description="List of filters to be applied to the resource",
    )

    def convert_to_query(self) -> Iterator[Q]:
        """
        Converts this rule's filters into a Django Q object query.
        Yields either a subquery Q or existence subquery, depending on the model.
        """
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
    """
    A ruleset combines multiple rules (or nested rulesets) using AND/OR logic.
    """

    condition: RulesetCondition = Field(
        default=RulesetCondition.AND,
        title="Logical condition",
        description="Logical condition used to chain the rules within the ruleset",
    )
    rules: List[Union[CohortRule, "CohortRuleset"]] = Field(
        title="Rules",
        description="List of rules or nested rulesets that define the fields and values to use for the filtering.",
    )

    def convert_to_query(self) -> Iterator[Q]:
        """
        Recursively converts this ruleset and its children into a Django Q object.
        """
        query = Q()
        for rule in self.rules:
            for rule_query in rule.convert_to_query():
                if self.condition == RulesetCondition.AND:
                    query = rule_query & query
                if self.condition == RulesetCondition.OR:
                    query = rule_query | query
        # Yield the completed, compiled logic for this branch of query back up the pipe:
        yield query


class CohortSchema(ModelGetSchema):
    """
    Schema for retrieving a cohort record.
    """

    population: int = Field(
        title="Population",
        description="Cohort population",
        alias="db_population",
        validation_alias=AliasChoices("db_population", "population"),
    )
    config = SchemaConfig(model=orm.Cohort)


class CohortCreateSchema(ModelCreateSchema):
    """
    Schema for creating a new cohort, including cohort logic definitions.
    """

    includeCriteria: Optional[CohortRuleset] = Field(
        default=None,
        title="Inclusion critera",
        description="Logic rules to filter and constrain the cases to be included in the cohort",
        alias="include_criteria",
        validation_alias=AliasChoices("includeCriteria", "include_criteria"),
    )
    excludeCriteria: Optional[CohortRuleset] = Field(
        default=None,
        title="Exclusion critera",
        description="Logic rules to filter and constrain the cases to be excluded from the cohort",
        alias="exclude_criteria",
        validation_alias=AliasChoices("excludeCriteria", "exclude_criteria"),
    )
    config = SchemaConfig(model=orm.Cohort)


class CohortFilters(create_filters_schema(schema=CohortSchema, name="CohortFilters")):
    """
    Additional filters for cohort listings.
    """

    createdBy: Optional[str] = Field(
        None, description="Filter for a particular cohort creator by its username"
    )

    def filter_createdBy(self, value: str) -> Q:
        """
        Adds a filter for the creator username.
        """
        return Q(created_by=self.createdBy) if value is not None else Q()


class CohortTraitAverage(Schema):
    """
    Descriptive statistics schema representing the average and optional standard deviation
    for a numeric cohort trait.
    """

    average: float = Field(
        title="Average", description="The mean value for the cohort trait."
    )
    standardDeviation: Optional[float] = Field(
        default=None,
        title="Standard Deviation",
        description="The standard deviation for the cohort trait, if applicable.",
    )


class CohortTraitMedian(Schema):
    """
    Descriptive statistics schema representing the median and interquartile range
    for a numeric cohort trait.
    """

    median: float = Field(
        title="Median", description="The median value for the cohort trait."
    )
    interQuartalRange: Tuple[float, float] = Field(
        title="Interquartile Range (IQR)",
        description="The lower and upper bounds of the interquartile range.",
    )


class CohortTraitCounts(Schema):
    """
    Frequency distribution schema for categorical cohort traits.
    """

    category: str = Field(
        title="Category",
        description="The category or group label for the cohort trait value.",
    )
    counts: int = Field(
        title="Counts", description="The number of records in this category."
    )
    percentage: float = Field(
        title="Percentage",
        description="The percentage of the total cohort population in this category.",
    )


class CohortTraits(Schema):

    age: CohortTraitMedian
    dataCompletion: CohortTraitMedian
    overallSurvival: Optional[CohortTraitMedian]
    ages: List[CohortTraitCounts]
    agesAtDiagnosis: List[CohortTraitCounts]
    genders: List[CohortTraitCounts]
    neoplasticSites: List[CohortTraitCounts]
    therapyLines: List[CohortTraitCounts]
    vitalStatus: List[CohortTraitCounts]


class CohortContribution(Schema):
    """
    Cohort contribution summary per contributor.
    """

    contributor: str = Field(
        title="Contributor",
        description="Username or identifier of the contributing user.",
    )
    contributions: int = Field(
        title="Contributions",
        description="The number of records or actions contributed by this user.",
    )


class KapplerMeierCurve(Schema):
    """
    Schema for Kaplan-Meier survival curve results.
    """

    months: List[float] = Field(
        title="Months",
        description="List of time points (in months) for survival probability estimates.",
    )
    probabilities: List[float] = Field(
        title="Probabilities", description="Survival probabilities at each time point."
    )
    lowerConfidenceBand: List[float] = Field(
        title="Lower Confidence Band",
        description="Lower bound of the survival probability confidence interval at each time point.",
    )
    upperConfidenceBand: List[float] = Field(
        title="Upper Confidence Band",
        description="Upper bound of the survival probability confidence interval at each time point.",
    )
