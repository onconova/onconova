from pop.oncology.models import PatientCase, PatientCaseDataCompletion
from pop.core.schemas import ModelSchema, CREATE_IGNORED_FIELDS
from pydantic import Field, AliasChoices

class PatientCaseDataCompletionSchema(ModelSchema):
    class Meta:
        name = 'PatientCaseDataCompletion'
        model = PatientCaseDataCompletion
        exclude = (
            'case',
        )

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
