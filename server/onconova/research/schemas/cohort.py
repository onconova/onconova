from enum import Enum
from typing import Any, Iterator, List, Tuple, Union

from django.db.models import Exists, OuterRef, Q
from ninja import Field, Schema
from pydantic import AliasChoices, field_validator

from onconova.core.measures import get_measure_db_value
from onconova.core.serialization import filters as filters_module
from onconova.core.serialization.factory import create_filters_schema
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.core.types import Nullable
from onconova.core.utils import camel_to_snake
from onconova.interoperability.schemas import ExportMetadata
from onconova.oncology import models as oncology_models
from onconova.research.models import cohort as orm


class RulesetCondition(str, Enum):
    """
    An enumeration representing logical conditions for rulesets.

    Attributes:
        AND (str): Represents the logical 'and' condition.
        OR (str): Represents the logical 'or' condition.
    """

    AND = "and"
    OR = "or"


# Dynamically create an Enum from oncology model class names
CohortQueryEntity = Enum(
    "CohortQueryEntity",
    {model.__name__: model.__name__ for model in oncology_models.MODELS},
    type=str,
)
"""Enumeration of case-related resource entities for cohort queries."""

# Dynamically create an Enum from available filter class names
CohortQueryFilter = Enum(
    "CohortQueryFilter",
    {filter.__name__: filter.__name__ for filter in filters_module.ALL_FILTERS},
    type=str,
)
"""Enumeration of available filter operators for cohort queries."""


class CohortRuleFilter(Schema):
    """
    Schema representing a filter rule for cohort queries.

    Attributes:
        field (str): Dot-separated path of the resource field (e.g. 'medications.drug').
        operator (CohortQueryFilter): Name of the filter operator to be applied to the field.
        value (Any): Filter value to be applied to the field using the rule's operator.
        db_value (Any): Returns the value formatted for database queries. If the value is a dictionary with 'unit' and 'value', it converts it using `get_measure_db_value`. If it contains 'start' and 'end', returns a tuple of (start, end). Otherwise, returns the value as-is.
        db_field (Any): Converts the dot-separated field path into Django ORM double-underscore syntax (e.g. 'medications.drug' -> 'medications__drug').
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
    def db_value(self):
        value = self.value
        if isinstance(value, dict):
            if "unit" in value and "value" in value:
                return get_measure_db_value(value=value["value"], unit=value["unit"])
            elif "start" in value and "end" in value:
                return (value["start"], value["end"])
        return value

    @property
    def db_field(self):
        """
        Converts a dot-separated field path into Django ORM double-underscore syntax.
        """
        return "__".join([camel_to_snake(step) for step in self.field.split(".")])


class CohortRule(Schema):
    """
    Represents a rule for cohort selection, specifying an entity and a set of filters.

    Attributes:
        entity (CohortQueryEntity): The case-related resource to which the rule applies.
        filters (List[CohortRuleFilter]): A list of filters to be applied to the resource.
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
        Converts the cohort filters into Django Q objects for querying the database.

        Iterates over the filters defined in the cohort, applies the corresponding operator
        to each filter, and combines them using logical AND. If the entity is a PatientCase,
        yields the combined Q object directly. Otherwise, constructs a subquery that filters
        related PatientCase objects and yields a Q object representing the existence of such
        cases.

        Yields:
            Iterator[Q]: An iterator of Django Q objects representing the query for the cohort.
        """
        model = getattr(oncology_models, self.entity)
        subquery = Q()
        for filter in self.filters:
            operator = getattr(filters_module, filter.operator)
            subquery = subquery & operator.get_query(
                filter.db_field, filter.db_value, model
            )
        if model is oncology_models.PatientCase:
            yield subquery
        else:
            subquery = model.objects.filter(Q(case=OuterRef("pk")) & subquery)
            yield Q(Exists(subquery))


class CohortRuleset(Schema):
    """
    Represents a set of cohort rules combined by a logical condition (AND/OR).

    Attributes:
        condition (RulesetCondition): Logical condition used to chain the rules within the ruleset.
        rules (List[Union[CohortRule, CohortRuleset]]): List of rules or nested rulesets that define the fields and values to use for filtering.
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
        Converts the ruleset into a Django Q object query iterator.

        Iterates through each rule in the ruleset, combining their queries using the specified logical condition
        (AND/OR). For each rule, its query is combined with the accumulated query using the condition. The final
        combined query is yielded as an iterator.

        Returns:
            Iterator[Q]: An iterator yielding the combined Q object representing the ruleset's logic.
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
    Schema for representing a Cohort entity.

    Attributes:
        population (int): The size of the cohort population. This field uses the database alias 'db_population' and supports validation using either 'db_population' or 'population'.

    Config:
        model (orm.Cohort): Specifies the ORM model associated with this schema.
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
    Schema for creating a Cohort instance.

    Attributes:
        includeCriteria (Optional[CohortRuleset]): Logic rules to filter and constrain the cases to be included in the cohort.
            - Title: Inclusion criteria
            - Description: Logic rules to filter and constrain the cases to be included in the cohort
            - Aliases: "includeCriteria", "include_criteria"

        excludeCriteria (Optional[CohortRuleset]): Logic rules to filter and constrain the cases to be excluded from the cohort.
            - Title: Exclusion criteria
            - Description: Logic rules to filter and constrain the cases to be excluded from the cohort
            - Aliases: "excludeCriteria", "exclude_criteria"

        config (SchemaConfig): Configuration for the schema, specifying the ORM model to use.
    """

    includeCriteria: Nullable[CohortRuleset] = Field(
        default=None,
        title="Inclusion critera",
        description="Logic rules to filter and constrain the cases to be included in the cohort",
        alias="include_criteria",
        validation_alias=AliasChoices("includeCriteria", "include_criteria"),
    )
    excludeCriteria: Nullable[CohortRuleset] = Field(
        default=None,
        title="Exclusion critera",
        description="Logic rules to filter and constrain the cases to be excluded from the cohort",
        alias="exclude_criteria",
        validation_alias=AliasChoices("excludeCriteria", "exclude_criteria"),
    )
    config = SchemaConfig(model=orm.Cohort)


class CohortFilters(create_filters_schema(schema=CohortSchema, name="CohortFilters")):

    createdBy: Nullable[str] = Field(
        None,
        title="Created by",
        description="Filter for a particular cohort creator by its username",
    )

    def filter_createdBy(self, value: str) -> Q:
        """
        Adds a filter for the creator username.
        """
        return Q(created_by=self.createdBy) if value is not None else Q()


class CohortTraitAverage(Schema):
    """
    Schema representing the average and standard deviation of a trait within a cohort.

    Attributes:
        average (float): The mean value for the cohort trait.
        standardDeviation (Optional[float]): The standard deviation for the cohort trait, if applicable. May be None.
    """

    average: float = Field(
        title="Average", description="The mean value for the cohort trait."
    )
    standardDeviation: Nullable[float] = Field(
        default=None,
        title="Standard Deviation",
        description="The standard deviation for the cohort trait, if applicable.",
    )


class CohortTraitMedian(Schema):
    """
    Schema representing the median and interquartile range (IQR) for a cohort trait.

    Attributes:
        median (float | None): The median value for the cohort trait.
        interQuartalRange (Tuple[float, float] | None): The lower and upper bounds of the interquartile range (IQR).
    """

    median: float | None = Field(
        default=None,
        title="Median",
        description="The median value for the cohort trait.",
    )
    interQuartalRange: Tuple[float, float] | None = Field(
        default=None,
        title="Interquartile Range (IQR)",
        description="The lower and upper bounds of the interquartile range.",
    )


class CohortTraitCounts(Schema):
    """
    Schema representing the count and percentage of records for a specific cohort trait category.

    Attributes:
        category (str): The category or group label for the cohort trait value.
        counts (int): The number of records in this category.
        percentage (float): The percentage of the total cohort population in this category.
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
    """
    Schema representing key traits and distributions within a patient cohort.

    Attributes:
        age (CohortTraitMedian): Median age of individuals in the cohort.
        dataCompletion (CohortTraitMedian): Median percentage of completed data per patient.
        overallSurvival (Nullable[CohortTraitMedian]): Median overall survival time in the cohort, if available.
        genders (List[CohortTraitCounts]): Distribution of genders within the cohort.
        neoplasticSites (List[CohortTraitCounts]): Distribution of neoplastic (tumor) sites in the cohort.
        therapyLines (List[CohortTraitCounts]): Distribution of therapy lines received by patients in the cohort.
        consentStatus (List[CohortTraitCounts]): Distribution of consent statuses for data use among cohort participants.
    """
    age: CohortTraitMedian = Field(
        ..., title="Age", description="Median age of individuals in the cohort."
    )
    dataCompletion: CohortTraitMedian = Field(
        ...,
        title="Data Completion",
        description="Median percentage of completed data per patient.",
    )
    overallSurvival: Nullable[CohortTraitMedian] = Field(
        title="Overall Survival",
        description="Median overall survival time in the cohort, if available.",
    )
    genders: List[CohortTraitCounts] = Field(
        ..., title="Genders", description="Distribution of genders within the cohort."
    )
    neoplasticSites: List[CohortTraitCounts] = Field(
        ...,
        title="Neoplastic Sites",
        description="Distribution of neoplastic (tumor) sites in the cohort.",
    )
    therapyLines: List[CohortTraitCounts] = Field(
        ...,
        title="Therapy Lines",
        description="Distribution of therapy lines received by patients in the cohort.",
    )
    consentStatus: List[CohortTraitCounts] = Field(
        ...,
        title="Consent Status",
        description="Distribution of consent statuses for data use among cohort participants.",
    )


class CohortContribution(Schema):
    """
    Schema representing a user's contribution to a cohort.

    Attributes:
        contributor (str): Username or identifier of the contributing user.
        contributions (int): The number of records or actions contributed by this user.
    """

    contributor: str = Field(
        title="Contributor",
        description="Username or identifier of the contributing user.",
    )
    contributions: int = Field(
        title="Contributions",
        description="The number of records or actions contributed by this user.",
    )


class ExportedCohortDefinition(ExportMetadata):
    """
    Represents an exported cohort definition along with its export metadata.

    Attributes:
        definition (CohortCreateSchema): The cohort definition, including its title and description.
    """
    definition: CohortCreateSchema = Field(
        title="Cohort Definition",
        description="The cohort definition",
    )
