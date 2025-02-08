from pop.oncology.models import Surgery
from pop.core.schemas import ModelSchema, CREATE_IGNORED_FIELDS
from pydantic import Field

class SurgerySchema(ModelSchema):
    description: str = Field(description='Human-readable description of the surgery') 

    class Meta:
        name = 'Surgery'
        model = Surgery
        fields = '__all__'

class SurgeryCreateSchema(ModelSchema):
    
    class Meta:
        name = 'SurgeryCreate'
        model = Surgery
        exclude = (
            *CREATE_IGNORED_FIELDS,
        )
