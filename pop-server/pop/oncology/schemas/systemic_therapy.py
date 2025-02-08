from pop.oncology.models import SystemicTherapy, SystemicTherapyMedication
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin
from ninja import Schema
from pydantic import Field, ConfigDict, BaseModel as PydanticBase
from typing import List 

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
    model_config = ConfigDict(title='SystemicTherapyMedication')

class SystemicTherapyMedicationCreateSchema(MedicationDynamicBase, CreateMixin):
    model_config = ConfigDict(title='SystemicTherapyMedicationCreate',)

class SystemicTherapySchema(SystemicTherapyDynamicBase, GetMixin):
    model_config = ConfigDict(title='SystemicTherapy')
    medications: List[SystemicTherapyMedicationSchema] = Field(description='Medications administered during the systemic therapy')

class SystemicTherapyCreateSchema(SystemicTherapyDynamicBase, CreateMixin):
    model_config = ConfigDict(title='SystemicTherapyCreate')