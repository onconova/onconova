from pop.oncology.models import PatientCase
from pop.core.schemas import ModelSchema, CREATE_IGNORED_FIELDS
from pydantic import Field 


class PatientCaseSchema(ModelSchema):
    age: int = Field(description='Approximate age of the patient in years') 

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
