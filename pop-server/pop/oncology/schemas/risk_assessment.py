from pop.oncology.models import RiskAssessment
from pop.core.schemas import ModelSchema, CREATE_IGNORED_FIELDS
from pydantic import Field

class RiskAssessmentSchema(ModelSchema):
    description: str = Field(description='Human-readable description of the tumor marker') 

    class Meta:
        name = 'RiskAssessment'
        model = RiskAssessment
        fields = '__all__'

class RiskAssessmentCreateSchema(ModelSchema):
    
    class Meta:
        name = 'RiskAssessmentCreate'
        model = RiskAssessment
        exclude = (
            *CREATE_IGNORED_FIELDS,
        )
