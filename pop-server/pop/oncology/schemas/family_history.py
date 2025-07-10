from pop.core.anonymization import AnonymizationConfig
from pop.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from pop.oncology import models as orm


class FamilyHistorySchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.FamilyHistory,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class FamilyHistoryCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.FamilyHistory)
