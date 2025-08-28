from onconova.core.anonymization import AnonymizationConfig
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.oncology import models as orm


class SurgerySchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.Surgery,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class SurgeryCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Surgery)
