from onconova.core.anonymization import AnonymizationConfig
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.oncology import models as orm


class TreatmentResponseSchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.TreatmentResponse,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class TreatmentResponseCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.TreatmentResponse)
