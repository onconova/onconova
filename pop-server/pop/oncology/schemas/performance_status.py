from pop.oncology.models import PerformanceStatus
from pop.core.schemas import ModelSchema, CodedConceptSchema, CREATE_IGNORED_FIELDS
from typing import Optional
from pydantic import Field, AliasChoices

class PerformanceStatusSchema(ModelSchema):
    description: str = Field(description='Human-readable description of the performance status') 
    ecogInterpretation: Optional[CodedConceptSchema] = Field(
            description='Official interpretation of the ECOG score',
            alias='ecog_interpretation',
            validation_alias=AliasChoices('ecogInterpretation', 'ecog_interpretation'),
    )
    karnofskyInterpretation: Optional[CodedConceptSchema] = Field(
        description='Official interpretation of the Karnofsky score',
        alias='karnofsky_interpretation',
        validation_alias=AliasChoices('karnofskyInterpretation', 'karnofsky_interpretation'),
    )
    
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
