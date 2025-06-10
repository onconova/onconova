from pydantic import Field
from typing import List 

from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.anonymization import AnonymizationConfig

class SystemicTherapyMedicationSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.SystemicTherapyMedication, exclude=['systemic_therapy'])

class SystemicTherapyMedicationCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.SystemicTherapyMedication, exclude=['systemic_therapy'])


class SystemicTherapySchema(ModelGetSchema):
    medications: List[SystemicTherapyMedicationSchema] = Field(description='Medications administered during the systemic therapy')
    duration: float = Field(description='Duration of treatment in days')
    config = SchemaConfig(model=orm.SystemicTherapy, anonymization=AnonymizationConfig(fields=['period'], key='caseId'))

class SystemicTherapyCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.SystemicTherapy, exclude=['is_adjunctive'])
