from ninja import Schema, Field
from typing import List, Dict, Literal, Any, Union, Optional
from enum import Enum 
from pop.oncology import models as oncology_models
from pop.core import filters as filters_module

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
    PERIOD = 'period'
    ENUM = 'enum'


CohortQueryEntity = Enum('CohortQueryEntity', {
    model.__name__.upper(): model.__name__ for model in oncology_models.MODELS
}, type=str)

CohortQueryFilter = Enum('CohortQueryFilter', {
    filter.__name__.upper(): filter.__name__ for filter in filters_module.__all__
}, type=str)


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
