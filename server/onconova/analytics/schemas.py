from datetime import date
from typing import List

from ninja import Field, Schema
from pydantic import ConfigDict

from onconova.core.schemas import CodedConcept
from onconova.core.types import Nullable


class DataPlatformStatistics(Schema):
    cases: int = Field(
        ...,
        title="Patient Cases",
        description="Total number of unique patient cases in the data platform.",
    )
    primarySites: int = Field(
        ...,
        title="Primary Sites",
        description="Number of distinct primary anatomical sites represented.",
    )
    projects: int = Field(
        ..., title="Projects", description="Total number of research projects."
    )
    cohorts: int = Field(
        ..., title="Cohorts", description="Number of defined cohorts in the platform."
    )
    entries: int = Field(
        ...,
        title="Data Entries",
        description="Total number of individual data entries recorded.",
    )
    mutations: int = Field(
        ...,
        title="Mutations",
        description="Total number of genetic mutations documented across all cases.",
    )
    clinicalCenters: int = Field(
        ...,
        title="Clinical Centers",
        description="Number of clinical centers contributing data.",
    )
    contributors: int = Field(
        ...,
        title="Contributors",
        description="Total number of individual data contributors.",
    )


class CountsPerMonth(Schema):
    month: date = Field(
        ...,
        title="Month",
        description="The month (as date) representing the period of data aggregation.",
    )
    cumulativeCount: int = Field(
        ...,
        title="Cumulative Case Count",
        description="Total number of entries accumulated up to and including the given month.",
    )


class EntityStatistics(Schema):
    population: Nullable[int] = Field(
        default=None, title="Population", description="Number of cases"
    )
    dataCompletionMedian: Nullable[float] = Field(
        default=None,
        title="Data Completion Median",
        description="Median percentage of case completion",
    )
    topographyCode: Nullable[str] = Field(
        default=None,
        title="Topography Code",
        description="ICD-O-3 topography code of the entity",
    )
    topographyGroup: Nullable[str] = Field(
        default=None,
        title="Topography Group",
        description="ICD-O-3 topography code of the entity group",
    )


class IncompleteCategory(Schema):
    category: str = Field(
        ...,
        title="Incomplete Category",
        description="The data category with cases where it is incomplete.",
    )
    cases: int = Field(
        ...,
        title="Affected Cases",
        description="Number of cases affected with the incomplete data category.",
    )
    affectedSites: List[CodedConcept] = Field(
        ...,
        title="Affected Sites",
        description="List of anatomical sites affected by this data incompleteness.",
    )


class DataCompletionStatistics(Schema):
    totalCases: int = Field(
        ...,
        title="Total Cases",
        description="Total number of patient cases analyzed for data completeness.",
    )
    overallCompletion: float = Field(
        ...,
        title="Overall Completion (%)",
        description="Overall percentage of data categories completed across all cases.",
    )
    mostIncompleteCategories: List[IncompleteCategory] = Field(
        ...,
        title="Most Incomplete Categories",
        description="List of the most common categories with missing data.",
    )
    completionOverTime: List[CountsPerMonth] = Field(
        ...,
        title="Completion Over Time",
        description="Historical trend of cumulative data completeness by month.",
    )
