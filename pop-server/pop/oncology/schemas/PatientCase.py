from pop.oncology.models import PatientCase
from pop.core.schemas import ModelSchema

class PatientCaseSchema(ModelSchema):
    
    class Meta:
        model = PatientCase
        fields = (
            'id',
            'pseudoidentifier',
            'race',
            'sex_at_birth',
            'gender_identity',
            'gender',
            'date_of_birth',
            'is_deceased',
            'date_of_death',
            'cause_of_death',
        )

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
