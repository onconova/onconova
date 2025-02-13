from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class SurgerySchema(ModelGetSchema):
    config = SchemaConfig(model=orm.Surgery)

class SurgeryCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Surgery)
