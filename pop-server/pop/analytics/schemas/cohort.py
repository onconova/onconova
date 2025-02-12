

from ninja import Schema, Field
from typing import Optional
from django.db.models import Q
from pop.core.schemas import create_schema, create_filters_schema, CREATE_IGNORED_FIELDS, GetMixin, CreateMixin
from pydantic import ConfigDict, AliasChoices

from pop.analytics.models import Cohort

CohortBase: Schema = create_schema(
    Cohort, 
    exclude=(*CREATE_IGNORED_FIELDS,),
)

class CohortSchema(CohortBase, GetMixin):
    population: int = Field(title='Population', description='Cohort population', alias='db_population', validation_alias=AliasChoices('db_population','population'))
    model_config = ConfigDict(title='Cohort')

class CohortCreateSchema(CohortBase, CreateMixin):
    model_config = ConfigDict(title='CohortCreate')

class CohortStatisticsSchema(Schema):
    ageAverage: Optional[float] = None
    ageStdDev: Optional[float] = None
    dataCompletionAverage: Optional[float] = None
    dataCompletionStdDev: Optional[float] = None
    model_config = ConfigDict(title='CohortStatistics')

CohortFiltersBase = create_filters_schema(
    schema = CohortSchema, 
    name='CohortFilters'
)

class CohortFilters(CohortFiltersBase):
    createdBy: Optional[str] = Field(None, description='Filter for a particular cohort creator by its username')

    def filter_createdBy(self, value: str) -> Q:
        return Q(created_by__username=self.createdBy) if value is not None else Q()
