from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class TreatmentResponseSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.TreatmentResponse)

class TreatmentResponseCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.TreatmentResponse)
