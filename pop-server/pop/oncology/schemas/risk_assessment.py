from pop.oncology import models as orm
from pop.core.serialization.metaclasses import (
    ModelGetSchema,
    ModelCreateSchema,
    SchemaConfig,
)
from typing_extensions import Self
from pop.oncology.models.risk_assessment import validate_risk_classification
from pop.core.anonymization import AnonymizationConfig
from pydantic import model_validator


class RiskAssessmentSchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.RiskAssessment,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )
    
    @model_validator(mode='after')
    def validate_risk_classification(self) -> Self:
        try:
            validate_risk_classification(self)
        except AssertionError:
            raise ValueError(f'{self.risk} is not a valid choice for risk methodology "{self.methodology}".')
        return self
    
class RiskAssessmentCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.RiskAssessment)
    
    @model_validator(mode='after')
    def validate_risk_classification(self) -> Self:
        try:
            validate_risk_classification(self)
        except AssertionError:
            raise ValueError(f'{self.risk} is not a valid choice for risk methodology "{self.methodology}".')
        return self

