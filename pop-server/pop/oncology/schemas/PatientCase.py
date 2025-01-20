from pop.oncology.models import PatientCase, PatientCaseDataCompletion
from datetime import datetime
from pop.core.schemas import ModelSchema, CREATE_IGNORED_FIELDS
from ninja import Schema
from pydantic import Field, AliasChoices
from typing import Optional

class PatientCaseDataCompletionStatusSchema(Schema):
    status: bool = Field(description='Boolean indicating whether the data category has been marked as completed')
    username: Optional[str] = Field(None,description='Username of the person who marked the category as completed')
    timestamp: Optional[datetime] = Field(None,description='Username of the person who marked the category as completed')

class PatientCaseSchema(ModelSchema):
    age: int = Field(description='Approximate age of the patient in years') 
    dataCompletionRate: float = Field(
        description='Percentage indicating the completeness of a case in terms of its data.', 
        alias='data_completion_rate',
        validation_alias=AliasChoices('dataCompletionRate', 'data_completion_rate'),
    ) 

    class Meta:
        name = 'PatientCase'
        model = PatientCase
        fields = '__all__'

class PatientCaseCreateSchema(ModelSchema):
    class Meta:
        name = 'PatientCaseCreate'
        model = PatientCase
        exclude = (
            *CREATE_IGNORED_FIELDS,
            'pseudoidentifier', 
            'is_deceased',
        )
