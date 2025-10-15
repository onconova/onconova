from typing import List, Self
from pydantic import Field, model_validator
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import risk_assessment as orm


class RiskAssessmentCreate(BaseSchema):
    
    __orm_model__ = orm.RiskAssessment 
    
    externalSource: Nullable[str] = Field(
        None,
        description='The digital source of the data, relevant for automated data',
        title='External data source',
    )
    externalSourceId: Nullable[str] = Field(
        None,
        description='The data identifier at the digital source of the data, relevant for automated data',
        title='External data source Id',
    )
    caseId: UUID = Field(
        ...,
        description="Indicates the case of the patient who's cancer risk is assesed",
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Clinically-relevant date at which the risk assessment was performed and recorded.',
        title='Assessment date',
    )
    methodology: CodedConcept = Field(
        ...,
        description='Indicates the method or type of risk assessment',
        title='Assessment methodology',
        json_schema_extra={'x-terminology': 'CancerRiskAssessmentMethod'},
    )
    risk: CodedConcept = Field(
        ...,
        description='Assessed risk',
        title='Risk',
        json_schema_extra={'x-terminology': 'CancerRiskAssessmentClassification'},
    )
    score: Nullable[float] = Field(
        None,
        description='Quantitative score used to classify the risk',
        title='Score',
    )
    assessedEntitiesIds: Nullable[List[UUID]] = Field(
        None,
        description='References to the neoplastic entities that were assessed to estimate the risk.',
        title='Assessed neoplastic entities',
    )

    @model_validator(mode="after")
    def validate_risk_classification(self) -> Self:
        try:
            orm.validate_risk_classification(self)
        except AssertionError:
            raise ValueError(f'{self.risk} is not a valid choice for risk methodology "{self.methodology}".')  # type: ignore
        return self


class RiskAssessment(RiskAssessmentCreate, MetadataAnonymizationMixin):

    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"