

from ninja import Schema, Field
from typing import List, Dict, Literal, Optional
from enum import Enum 

from pop.oncology.models  import (
    NeoplasticEntity,
    TNMStaging,
)

class RulesetCondition(Enum):
    AND = 'and'
    OR = 'or'




class CohortBuilderField(Schema):
    name: str
    operators: List[str]
    type: str
    entity: str
    options: Optional[List[Dict]] = None

class CohortBuilderEntity(Schema):
    name: str

class CohortBuilderConfig(Schema):
    allowEmptyRulesets: Literal[False] = False
    fields: Dict[str, CohortBuilderField]
    entities: Dict[str, CohortBuilderEntity]

# class CohortFilterRuleSchema(Schema):
#     entity: str
#     field: str
#     filter: str
#     value: any

# class CohortFilterSchema(Schema):
#     condition: RulesetCondition
#     rules: CohortFilterRuleSchema