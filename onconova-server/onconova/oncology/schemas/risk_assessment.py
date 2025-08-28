from pydantic import model_validator
from typing_extensions import Self

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.oncology import models as orm
from onconova.oncology.models.risk_assessment import validate_risk_classification


class RiskAssessmentSchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.RiskAssessment,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )

    @model_validator(mode="after")
    def validate_risk_classification(self) -> Self:
        try:
            validate_risk_classification(self)
        except AssertionError:
            raise ValueError(f'{self.risk} is not a valid choice for risk methodology "{self.methodology}".')  # type: ignore
        return self


class RiskAssessmentCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.RiskAssessment)

    @model_validator(mode="after")
    def validate_risk_classification(self) -> Self:
        try:
            validate_risk_classification(self)
        except AssertionError:
            raise ValueError(f'{self.risk} is not a valid choice for risk methodology "{self.methodology}".')  # type: ignore
        return self
