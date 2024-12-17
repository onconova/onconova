from pop.oncology.models import SystemicTherapy
from pop.core.schemas import ModelSchema, CREATE_IGNORED_FIELDS
from pydantic import Field
from typing import List 


class SystemicTherapySchema(ModelSchema):
    description: str = Field(description='Human-readable description of the systemic therapy') 
    class Meta:
        name = 'SystemicTherapy'
        model = SystemicTherapy
        fields = '__all__'
        reverse_fields = [
            'medications',
        ] 
        expand = {
            'medications': 'SystemicTherapyMedication'
        }

class SystemicTherapyCreateSchema(ModelSchema):
    class Meta:
        name = 'SystemicTherapyCreate'
        model = SystemicTherapy
        exclude = (
            *CREATE_IGNORED_FIELDS,
        )
        reverse_fields = [
            'medications',
        ] 
        expand = {
            'medications': 'SystemicTherapyMedicationCreate'
        }
