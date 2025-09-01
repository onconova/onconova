"""
This module defines Pydantic schemas for representing key statistics, data completeness, and entity information
within the Onconova data platform. The schemas are used for API serialization and validation of analytics-related
data, including platform-wide statistics, monthly counts, entity-level statistics, and data completion metrics.
"""
from datetime import date

from typing import List

from ninja import Field, Schema
from pydantic import ConfigDict

from onconova.core.schemas import CodedConcept
from onconova.core.types import Nullable


class DataPlatformStatistics(Schema):
    """
    Schema representing key statistics of the data platform.

    Attributes:
        cases (int): Total number of unique patient cases in the data platform.
        primarySites (int): Number of distinct primary anatomical sites represented.
        projects (int): Total number of research projects.
        cohorts (int): Number of defined cohorts in the platform.
        entries (int): Total number of individual data entries recorded.
        mutations (int): Total number of genetic mutations documented across all cases.
        clinicalCenters (int): Number of clinical centers contributing data.
        contributors (int): Total number of individual data contributors.
    """
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
    """
    Schema representing the cumulative count of entries per month.

    Attributes:
        month (date): The month (as a date object) representing the period of data aggregation.
        cumulativeCount (int): Total number of entries accumulated up to and including the given month.
    """
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
    """
    Schema representing statistical data for a medical entity.

    Attributes:
        population (Optional[int]): Number of cases in the population.
        dataCompletionMedian (Optional[float]): Median percentage of case completion.
        topographyCode (Optional[str]): ICD-O-3 topography code of the entity.
        topographyGroup (Optional[str]): ICD-O-3 topography code of the entity group.
    """
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
    """
    Schema representing a category of data incompleteness.

    Attributes:
        category (str): The data category with cases where it is incomplete.
        cases (int): Number of cases affected with the incomplete data category.
        affectedSites (List[CodedConcept]): List of anatomical sites affected by this data incompleteness.
    """
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
    """
    Schema representing statistics on data completion for patient cases.

    Attributes:
        totalCases (int): Total number of patient cases analyzed for data completeness.
        overallCompletion (float): Overall percentage of data categories completed across all cases.
        mostIncompleteCategories (List[IncompleteCategory]): List of the most common categories with missing data.
        completionOverTime (List[CountsPerMonth]): Historical trend of cumulative data completeness by month.
    """
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
