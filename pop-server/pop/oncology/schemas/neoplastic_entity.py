from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class NeoplasticEntitySchema(ModelGetSchema):
    config = SchemaConfig(model=orm.NeoplasticEntity)

class NeoplasticEntityCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.NeoplasticEntity)
