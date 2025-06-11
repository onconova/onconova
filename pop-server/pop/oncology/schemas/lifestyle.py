from pop.oncology import models as orm
from pop.core.serialization.metaclasses import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.anonymization import AnonymizationConfig

class LifestyleSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.Lifestyle, anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class LifestyleCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Lifestyle)