

from ninja import Schema, Field
from typing import Optional, Tuple
from django.db.models import Q
from pydantic import ConfigDict, AliasChoices

from django.db.models import Avg, Count, StdDev
from pop.analytics import models as orm
from pop.core.schemas import UserSchema
from pop.core.schemas.factory import create_filters_schema
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class CohortSchema(ModelGetSchema):
    population: int = Field(title='Population', description='Cohort population', alias='db_population', validation_alias=AliasChoices('db_population','population'))
    config = SchemaConfig(model=orm.Cohort)

class CohortCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Cohort)

class CohortStatisticsSchema(Schema):
    ageAverage: Optional[float] = None
    ageStdDev: Optional[float] = None
    dataCompletionAverage: Optional[float] = None
    dataCompletionStdDev: Optional[float] = None
    model_config = ConfigDict(title='CohortStatistics')

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
    contributor: UserSchema
    contributions: int

CohortFiltersBase = create_filters_schema(
    schema = CohortSchema, 
    name='CohortFilters'
)

class CohortFilters(CohortFiltersBase):
    createdBy: Optional[str] = Field(None, description='Filter for a particular cohort creator by its username')

    def filter_createdBy(self, value: str) -> Q:
        return Q(created_by__username=self.createdBy) if value is not None else Q()
