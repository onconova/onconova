from pydantic import Field
from uuid import UUID
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept
from onconova.core.types import Nullable
from onconova.oncology.models import family_history as orm

class FamilyHistoryCreate(BaseSchema):
    
    __orm_model__ = orm.FamilyHistory
    
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
        description="Indicates the case of the patient who's family's history is being recorded",
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description="Clinically-relevant date at which the patient's family history was assessed and recorded.",
        title='Assessment date',
    )
    relationship: CodedConcept = Field(
        ...,
        description='Relationship to the patient',
        title='Relationship',
        json_schema_extra={'x-terminology': 'FamilyMemberType'},
    )
    hadCancer: bool = Field(
        ...,
        description='Whether the family member has a history of cancer',
        title='Had cancer',
    )
    contributedToDeath: Nullable[bool] = Field(
        None,
        description='Whether the cancer contributed to the cause of death of the family member',
        title='Contributed to death',
    )
    onsetAge: Nullable[int] = Field(
        None,
        description="Age at which the family member's cancer manifested",
        title='Onset age',
    )
    topography: Nullable[CodedConcept] = Field(
        None,
        description="Estimated or actual topography of the family member's cancer",
        title='Topography',
        json_schema_extra={'x-terminology': 'CancerTopography'},
    )
    morphology: Nullable[CodedConcept] = Field(
        None,
        description="Morphology of the family member's cancer (if known)",
        title='Morphology',
        json_schema_extra={'x-terminology': 'CancerMorphology'},
    )


class FamilyHistory(FamilyHistoryCreate, MetadataAnonymizationMixin):

    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"