from pop.oncology.models import CancerPatient
from pop.core.schemas import ModelSchema

class CancerPatientSchema(ModelSchema):
    
    class Meta:
        model = CancerPatient
        fields = (
            'id',
            'pseudoidentifier',
            'race',
            'birthsex',
            'gender_identity',
            'gender',
            'birthdate',
            'is_deceased',
            'date_of_death',
        )

class CancerPatientCreateSchema(ModelSchema):
    
    class Meta:
        model = CancerPatient
        exclude = ('id', 'created_at', 'updated_at', 'pseudoidentifier', 'created_by', 'updated_by')
