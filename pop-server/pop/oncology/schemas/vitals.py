from typing import Optional
from ninja import Field

from pop.oncology import models as orm
from pop.core.measures import Measure
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.anonymization import AnonymizationConfig

class VitalsSchema(ModelGetSchema):
    body_mass_index: Optional[Measure] = Field(None, description='Bodymass index of the patient')
    config = SchemaConfig(model=orm.Vitals, exclude=('body_mass_index',), anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class VitalsCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Vitals, exclude=('body_mass_index',))
