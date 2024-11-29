from pop.oncology.models import PatientCase
from pop.core.schemas import ModelSchema
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
            'id', 
            'created_at', 
            'updated_at', 
            'pseudoidentifier', 
            'created_by', 
            'updated_by',
            'is_deceased',
        )
