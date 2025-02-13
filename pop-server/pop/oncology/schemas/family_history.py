from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class FamilyHistorySchema(ModelGetSchema):
    config = SchemaConfig(model=orm.FamilyHistory)
    
class FamilyHistoryCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.FamilyHistory)
