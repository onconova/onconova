from pop.oncology import models as orm
from pop.core.serialization.metaclasses import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.anonymization import AnonymizationConfig

class TumorMarkerSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.TumorMarker, anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class TumorMarkerCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.TumorMarker)
