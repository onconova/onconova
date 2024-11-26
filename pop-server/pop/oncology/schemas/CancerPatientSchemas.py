from pop.oncology.models import CancerPatient
from pop.core.schemas import ModelSchema

class CancerPatientSchema(ModelSchema):
    
    class Meta:
        model = CancerPatient
        fields = '__all__'

class CancerPatientCreateSchema(ModelSchema):
    
    class Meta:
        model = CancerPatient
        exclude = ('id', 'created_at', 'updated_at', 'pseudoidentifier', 'created_by', 'updated_by')
