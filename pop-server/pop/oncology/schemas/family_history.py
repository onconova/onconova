from pop.oncology import models as orm
from pop.core.serialization.metaclasses import (
    ModelGetSchema,
    ModelCreateSchema,
    SchemaConfig,
)
from pop.core.anonymization import AnonymizationConfig


class FamilyHistorySchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.FamilyHistory,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class FamilyHistoryCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.FamilyHistory)
