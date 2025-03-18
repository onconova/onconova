
from datetime import date
from ninja import Schema, Field
from typing import List, Dict, Literal, Optional, Any, Union
from pydantic import ConfigDict

class DataPlatformStatisticsSchema(Schema):
    cases: int
    primarySites: int
    projects: int 
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
    contributors: Optional[List[str]] = None
    model_config = ConfigDict(title='EntityStatistics')