from typing import List
from pydantic import Field
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import surgery as orm

class SurgeryCreate(BaseSchema):
    
    __orm_model__ = orm.Surgery
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
        description='Indicates the case of the patient who received the surgical procedure',
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Clinically-relevant date of the surgical procedure.',
        title='Assessment date',
    )
    procedure: CodedConcept = Field(
        ...,
        description='The specific surgical procedure that was performed',
        title='Surgical procedure',
        json_schema_extra={'x-terminology': 'SurgicalProcedure'},
    )
    intent: orm.SurgeryIntentChoices = Field(
        ...,
        description='Therapeutic intent of the surgery',
        title='Intent',
    )
    bodysite: Nullable[CodedConcept] = Field(
        None,
        description='Anatomical location of the surgery',
        title='Anatomical location',
        json_schema_extra={'x-terminology': 'CancerTopography'},
    )
    bodysiteQualifier: Nullable[CodedConcept] = Field(
        None,
        description='General qualifier for the anatomical location of the surgery',
        title='Anatomical location qualifier',
        json_schema_extra={'x-terminology': 'BodyLocationQualifier'},
    )
    bodysiteLaterality: Nullable[CodedConcept] = Field(
        None,
        description='Laterality for the anatomical location of the surgery',
        title='Anatomical location laterality',
        json_schema_extra={'x-terminology': 'LateralityQualifier'},
    )
    outcome: Nullable[CodedConcept] = Field(
        None,
        description='The outcome of the surgery',
        title='Outcome',
        json_schema_extra={'x-terminology': 'ProcedureOutcome'},
    )
    therapyLineId: Nullable[UUID] = Field(
        None,
        description='Therapy line to which the surgery is assigned to',
        title='Therapy line',
    )
    targetedEntitiesIds: Nullable[List[UUID]] = Field(
        None,
        description='References to the neoplastic entities that were targeted by the surgery',
        title='Targeted neoplastic entities',
    )

class Surgery(SurgeryCreate, MetadataAnonymizationMixin):
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
