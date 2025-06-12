from pop.oncology import models as orm
from pop.core.serialization.metaclasses import (
    ModelGetSchema,
    ModelCreateSchema,
    SchemaConfig,
)
from pop.core.anonymization import AnonymizationConfig


class RiskAssessmentSchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.RiskAssessment,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class RiskAssessmentCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.RiskAssessment)
