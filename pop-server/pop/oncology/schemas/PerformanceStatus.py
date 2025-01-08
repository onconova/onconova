from pop.oncology.models import PerformanceStatus
from pop.core.schemas import ModelSchema, CodedConceptSchema, CREATE_IGNORED_FIELDS
from typing import Optional
from pydantic import Field

class PerformanceStatusSchema(ModelSchema):
    description: str = Field(description='Human-readable description of the performance status') 
    ecog_interpretation: Optional[CodedConceptSchema] = Field(description='Official interpretation of the ECOG score')
    karnofsky_interpretation: Optional[CodedConceptSchema] = Field(description='Official interpretation of the Karnofsky score')
    
    class Meta:
        name = 'PerformanceStatus'
        model = PerformanceStatus
        fields = '__all__'

class PerformanceStatusCreateSchema(ModelSchema):
    
    class Meta:
        name = 'PerformanceStatusCreate'
        model = PerformanceStatus
        exclude = (
            *CREATE_IGNORED_FIELDS,
        )
