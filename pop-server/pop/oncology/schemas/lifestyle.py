from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class LifestyleSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.Lifestyle)

class LifestyleCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Lifestyle)