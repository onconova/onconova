from datetime import date
from typing import Any, Dict, List, Literal, Optional, Union

from ninja import Field, Schema
from pop.core.schemas import CodedConcept
from pydantic import ConfigDict


class DataPlatformStatisticsSchema(Schema):
    cases: int
    primarySites: int
    projects: int
    cohorts: int
    entries: int
    mutations: int
    clinicalCenters: int
    contributors: int


class CasesPerMonthSchema(Schema):
    month: date
    cumulativeCount: int


class EntityStatisticsSchema(Schema):
    population: Optional[int] = None
    dataCompletionMedian: Optional[float] = None
    topographyCode: Optional[str] = None
    topographyGroup: Optional[str] = None
    model_config = ConfigDict(title="EntityStatistics")


class IncompleteCategory(Schema):
    category: str
    cases: int
    affectedSites: List[CodedConcept]


class DataCompletionStatistics(Schema):
    totalCases: int
    overallCompletion: float
    mostIncompleteCategories: List[IncompleteCategory]
    completionOverTime: List
