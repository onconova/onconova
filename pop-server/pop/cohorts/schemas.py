

from ninja import Schema, Field
from typing import List, Dict, Literal, Optional, Any, Union
from enum import Enum 
from django.db.models import Q
from pop.oncology import models as oncology_models
from pop.core.schemas import filters as filters_module
from pop.core.schemas import create_schema, create_filters_schema, CREATE_IGNORED_FIELDS, GetMixin, CreateMixin
from pydantic import ConfigDict, AliasChoices

from pop.cohorts.models import Cohort

class RulesetCondition(str, Enum):
    AND = 'and'
    OR = 'or'

class CohortRuleType(str, Enum):
    STRING = 'string'
    NUMBER = 'number'
    DATE = 'date'
    BOOLEAN = 'boolean'
    CODED_CONCEPT = 'coded_concept'
    MEASURE = 'measure'
    ENUM = 'enum'


CohortQueryEntity = Enum('CohortQueryEntity', {
    model.__name__.upper(): model.__name__ for model in oncology_models.__all__
}, type=str)


CohortQueryFilter = Enum('CohortQueryFilter', {
    filter.__name__.upper(): filter.__name__ for filter in filters_module.__all__
}, type=str)



class CohortFilterRule(Schema):
    entity: CohortQueryEntity # type: ignore
    field: str
    operator: CohortQueryFilter # type: ignore
    value: Any

class CohortFilterRuleset(Schema):
    condition: RulesetCondition = RulesetCondition.AND
    rules: List[Union[CohortFilterRule, 'CohortFilterRuleset']]


class CohortFilter(Schema):
    include: Optional[CohortFilterRuleset] = Field(None, title='Inclusion criteria')
    exclude: Optional[CohortFilterRuleset] = Field(None, title='Exclusion criteria')


class CohortBuilderFieldOption(Schema):
    name: str
    value: Any

class CohortBuilderField(Schema):
    name: str
    operators: List[CohortQueryFilter] # type: ignore
    type: CohortRuleType
    entity: CohortQueryEntity # type: ignore
    options: List[CohortBuilderFieldOption] = []

class CohortBuilderEntity(Schema):
    name: str

class CohortBuilderConfig(Schema):
    allowEmptyRulesets: Literal[False] = False
    fields: Dict[str, CohortBuilderField]
    entities: Dict[str, CohortBuilderEntity]




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
