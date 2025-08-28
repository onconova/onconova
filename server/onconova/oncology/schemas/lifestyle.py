from onconova.core.anonymization import AnonymizationConfig
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.oncology import models as orm


class LifestyleSchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.Lifestyle,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class LifestyleCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Lifestyle)
