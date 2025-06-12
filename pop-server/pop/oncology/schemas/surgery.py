from pop.oncology import models as orm
from pop.core.serialization.metaclasses import (
    ModelGetSchema,
    ModelCreateSchema,
    SchemaConfig,
)
from pop.core.anonymization import AnonymizationConfig


class SurgerySchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.Surgery,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class SurgeryCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Surgery)
