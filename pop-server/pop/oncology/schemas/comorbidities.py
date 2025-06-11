from ninja import Schema, Field
from typing import Optional, List
from pydantic import AliasChoices

from pop.oncology import models as orm
from pop.core.schemas import CodedConcept as CodedConceptSchema
from pop.core.serialization.metaclasses import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.anonymization import AnonymizationConfig

class ComorbiditiesAssessmentSchema(ModelGetSchema):
    score: Optional[int | float] = Field(default=None, alias='score', description='Comorbidity score')
    config = SchemaConfig(model=orm.ComorbiditiesAssessment, anonymization=AnonymizationConfig(fields=['date'], key='caseId'))    
    
class ComorbiditiesAssessmentCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.ComorbiditiesAssessment)    

class ComorbidityPanelCategory(Schema):
    label: str = Field(description='Label of the comorbidity panel category')
    default: Optional[CodedConceptSchema] = Field(None, description='Default choice for category')
    conditions: List[CodedConceptSchema] = Field(description='List of conditions included in the panel category')

class ComorbiditiesPanel(Schema):
    name: str = Field(description='Comorbidity panel name')
    categories: List[ComorbidityPanelCategory] = Field(None, description='Comorbidity panel categories')
    