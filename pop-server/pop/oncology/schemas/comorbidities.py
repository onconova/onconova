from pop.oncology.models import ComorbiditiesAssessment
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ConfigDict, CodedConceptSchema
from ninja import Schema, Field
from typing import Optional, List


ComorbiditiesAssessmentBase: Schema = create_schema(
    ComorbiditiesAssessment, 
    exclude=(*CREATE_IGNORED_FIELDS,),
)

class ComorbidityPanelCategory(Schema):
    label: str
    default: CodedConceptSchema = Field(description='Default choice for category')
    conditions: List[CodedConceptSchema]

class ComorbiditiesAssessmentSchema(ComorbiditiesAssessmentBase, GetMixin):
    index: Optional[int] | float = Field(None, description='Comorbidity score')
    model_config = ConfigDict(title='ComorbiditiesAssessment')
    
class ComorbiditiesAssessmentCreateSchema(ComorbiditiesAssessmentBase, CreateMixin):
    model_config = ConfigDict(title='ComorbiditiesAssessmentCreate')
    
class ComorbiditiesPanelSchema(Schema):
    name: str = Field(description='Comorbidity panel name')
    categories: List[ComorbidityPanelCategory] = Field(None, description='Comorbidity panel categories')
    model_config = ConfigDict(title='ComorbiditiesPanel')
    