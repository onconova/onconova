from typing import List
from pydantic import Field
from uuid import UUID
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, MetadataMixin, CodedConcept
from onconova.core.types import Nullable
from onconova.oncology.models import adverse_event as orm

class AdverseEventSuspectedCauseCreate(BaseSchema):
    
    __orm_model__ = orm.AdverseEventSuspectedCause
    
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
    systemicTherapyId: Nullable[UUID] = Field(
        None,
        description='Systemic therapy suspected to be the cause of the adverse event',
        title='Suspected systemic therapy',
    )
    medicationId: Nullable[UUID] = Field(
        None,
        description='Systemic therapy medication suspected to be the cause of the adverse event',
        title='Suspected systemic therapy medication',
    )
    radiotherapyId: Nullable[UUID] = Field(
        None,
        description='Radiotherapy suspected to be the cause of the adverse event',
        title='Suspected radiotherapy',
    )
    surgeryId: Nullable[UUID] = Field(
        None,
        description='Surgery suspected to be the cause of the adverse event',
        title='Suspected surgery',
    )
    causality: Nullable[orm.AdverseEventSuspectedCauseCausalityChoices] = Field(
        None,
        description='Assessment of the potential causality',
        title='Causality',
    )

class AdverseEventSuspectedCause(AdverseEventSuspectedCauseCreate, MetadataMixin):
    pass

class AdverseEventMitigationCreate(BaseSchema):
    
    __orm_model__ = orm.AdverseEventMitigation
    
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
    category: orm.AdverseEventMitigationCategoryChoices = Field(
        ...,
        description='Type of mitigation employed',
        title='Mitigation category',
    )
    adjustment: Nullable[CodedConcept] = Field(
        None,
        description='Classification of the adjustment of systemic anti-cancer treatment used to mitigate the adverse event (if applicable)',
        title='Treatment Adjustment',
        json_schema_extra={'x-terminology': 'AdverseEventMitigationTreatmentAdjustment'},
    )
    drug: Nullable[CodedConcept] = Field(
        None,
        description='Classification of the pharmacological treatment used to mitigate the adverse event (if applicable)',
        title='Pharmacological drug',
        json_schema_extra={'x-terminology': 'AdverseEventMitigationDrug'},
    )
    procedure: Nullable[CodedConcept] = Field(
        None,
        description='Classification of the non-pharmacological procedure used to mitigate the adverse event (if applicable)',
        title='Procedure',
        json_schema_extra={'x-terminology': 'AdverseEventMitigationProcedure'},
    )
    management: Nullable[CodedConcept] = Field(
        None,
        description='Management type of the adverse event mitigation',
        title='Management',
        json_schema_extra={'x-terminology': 'AdverseEventMitigationManagement'},
    )

class AdverseEventMitigation(AdverseEventMitigationCreate, MetadataMixin):
    pass



class AdverseEventCreate(BaseSchema):
    
    __orm_model__ = orm.AdverseEvent
    
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
        description='Indicates the case of the patient who had the adverse event being recorded',
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Clinically-relevant date at which the adverse event ocurred.',
        title='Event date',
    )
    event: CodedConcept = Field(
        ...,
        description='Classification of the adverse event using CTCAE criteria',
        title='Adverse event',
        json_schema_extra={'x-terminology': 'AdverseEventTerm'},
    )
    grade: int = Field(
        ...,
        description='The grade associated with the severity of an adverse event, using CTCAE criteria.',
        title='Grade',
    )
    outcome: orm.AdverseEventOutcomeChoices = Field(
        ...,
        description='The date when the adverse event ended or returned to baseline.',
        title='Date resolved',
    )
    dateResolved: Nullable[date_aliased] = Field(
        None,
        description='The date when the adverse event ended or returned to baseline.',
        title='Date resolved',
    )


class AdverseEvent(AdverseEventCreate, MetadataAnonymizationMixin):
    
    suspectedCauses: List[AdverseEventSuspectedCause] = Field(
        title="Suspected causes",
        description="Suspected causes of the adverse event",
    )
    mitigations: List[AdverseEventMitigation] = Field(
        title="Mitigations",
        description="Mitigations of the adverse event",
    )
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"    
