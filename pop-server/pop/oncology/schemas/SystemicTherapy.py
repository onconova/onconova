from pop.oncology.models import SystemicTherapy, SystemicTherapyMedication
from pop.core.schemas import ModelSchema, CREATE_IGNORED_FIELDS, create_schema
from ninja import Schema
from pydantic import Field, ConfigDict, BaseModel as PydanticBase
from typing import List 

from pop.core.models import BaseModel

BaseModelSchema = create_schema(
    BaseModel, 
    name='BaseModel',
    fields=(*CREATE_IGNORED_FIELDS,),
)

class GetMixin(BaseModelSchema):
    description: str = Field(description='Human-readable description') 
    
class CreateMixin(PydanticBase):
    pass        



MedicationDynamicBase: Schema = create_schema(
    SystemicTherapyMedication, 
    name='SystemicTherapyMedicationCreate',
    exclude=(*CREATE_IGNORED_FIELDS, 'systemic_therapy'),
)

SystemicTherapyDynamicBase: Schema = create_schema(
    SystemicTherapy, 
    name='SystemicTherapyCreate',
    exclude=(*CREATE_IGNORED_FIELDS,),
)

class SystemicTherapyMedicationSchema(MedicationDynamicBase, GetMixin):
    # Schema config
    model_config = ConfigDict(
        title='SystemicTherapyMedication',
    )

class SystemicTherapyMedicationCreateSchema(MedicationDynamicBase, CreateMixin):
    # Schema config
    model_config = ConfigDict(
        title='SystemicTherapyMedicationCreate',
    )

class SystemicTherapySchema(SystemicTherapyDynamicBase, GetMixin):
    medications: List[SystemicTherapyMedicationSchema] = Field(description='Medications administered during the systemic therapy')
    # Schema config
    model_config = ConfigDict(
        title='SystemicTherapy',
    )

class SystemicTherapyCreateSchema(SystemicTherapyDynamicBase, CreateMixin):
    # Schema config
    model_config = ConfigDict(
        title='SystemicTherapyCreate',
    )