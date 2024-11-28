from pop.oncology.models import PatientCase
from pop.core.schemas import ModelSchema, UserSchema
from typing import List
from pydantic import Field 


class PatientCaseSchema(ModelSchema):
    age: int = Field(description='Approximate age of the patient in years') 

    class Meta:
        model = PatientCase
        fields = '__all__'

class PatientCaseCreateSchema(ModelSchema):
    
    class Meta:
        model = PatientCase
        exclude = (
            'id', 
            'created_at', 
            'updated_at', 
            'pseudoidentifier', 
            'created_by', 
            'updated_by',
            'is_deceased',
        )
