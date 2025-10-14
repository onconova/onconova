from pydantic import Field
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, Period
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import therapy_line as orm


class TherapyLineCreate(BaseSchema):
    
    __orm_model__ = orm.TherapyLine 
    
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
        description='Indicates the case of the patient to whom this therapy line is associated',
        title='Patient case',
    )
    ordinal: int = Field(
        ...,
        description='Number indicating the sequence in which this block of treatments were administered to the patient',
        title='Line ordinal number',
    )
    intent: orm.TherapyLineIntentChoices = Field(
        ...,
        description='Treatment intent of the system therapy',
        title='Intent',
    )
    progressionDate: Nullable[date_aliased] = Field(
        None,
        description='Date at which progression was first detected, if applicable',
        title='Begin of progression',
    )


class TherapyLine(TherapyLineCreate, MetadataAnonymizationMixin):
    
    period: Nullable[Period] = Field(
        default=None,
        title="Period",
        description="Time period of the therapy line",
        alias="period",
    )
    label: str = Field(
        title="Label",
        description="Label categorizing the therapy line",
        alias="label",
    )
    progressionFreeSurvival: Nullable[float] = Field(
        default=None,
        title="Progression-free survival in months",
        description="Progression-free survival (PFS) of the patient for the therapy line",
    )
    
    __anonymization_fields__ = ("period",)
    __anonymization_key__ = "caseId"