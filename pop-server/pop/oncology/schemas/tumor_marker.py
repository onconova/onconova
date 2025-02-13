from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class TumorMarkerSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.TumorMarker)

class TumorMarkerCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.TumorMarker)
