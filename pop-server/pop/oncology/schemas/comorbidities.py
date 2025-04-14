from ninja import Schema, Field
from typing import Optional, List
from pydantic import AliasChoices

from pop.oncology import models as orm
from pop.core.schemas import CodedConceptSchema
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class ComorbiditiesAssessmentSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.ComorbiditiesAssessment)    
    score: Optional[int | float] = Field(default=None, alias='score', description='Comorbidity score')
    
class ComorbiditiesAssessmentCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.ComorbiditiesAssessment)    

class ComorbidityPanelCategory(Schema):
    label: str = Field(description='Label of the comorbidity panel category')
    default: Optional[CodedConceptSchema] = Field(None, description='Default choice for category')
    conditions: List[CodedConceptSchema] = Field(description='List of conditions included in the panel category')

class ComorbiditiesPanel(Schema):
    name: str = Field(description='Comorbidity panel name')
    categories: List[ComorbidityPanelCategory] = Field(None, description='Comorbidity panel categories')
    