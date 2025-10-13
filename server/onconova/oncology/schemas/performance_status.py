from datetime import date as date_aliased
from uuid import UUID
from pydantic import AliasChoices, Field

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.schemas import BaseSchema, MetadataSchemaMixin, CodedConcept
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.core.types import Nullable
from onconova.oncology import models as orm


class PerformanceStatusCreate(BaseSchema):
    
    __orm_model__ = orm.PerformanceStatus 
    
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
        description="Indicates the case of the patient who's performance status is assesed",
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Clinically-relevant date at which the performance score was performed and recorded.',
        title='Assessment date',
    )
    ecogScore: Nullable[int] = Field(
        None,
        description='ECOG Performance Status Score',
        title='ECOG Score',
    )
    karnofskyScore: Nullable[int] = Field(
        None,
        description='Karnofsky Performance Status Score',
        title='Karnofsky Score',
    )

class PerformanceStatus(PerformanceStatusCreate, MetadataSchemaMixin):
    
    ecogInterpretation: Nullable[CodedConcept] = Field(
        default=None,
        title="ECOG Interpreation",
        description="Official interpretation of the ECOG score",
        json_schema_extra={"x-terminology": "ECOGPerformanceStatusInterpretation"},
    )
    karnofskyInterpretation: Nullable[CodedConcept] = Field(
        default=None,
        title="Karnofsky Interpreation",
        description="Official interpretation of the Karnofsky score",
        json_schema_extra={"x-terminology": "KarnofskyPerformanceStatusInterpretation"},
    )
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"

