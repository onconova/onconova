from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class RiskAssessmentSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.RiskAssessment)

class RiskAssessmentCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.RiskAssessment)
