from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.anonymization import AnonymizationConfig

class TreatmentResponseSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.TreatmentResponse, anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class TreatmentResponseCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.TreatmentResponse)
