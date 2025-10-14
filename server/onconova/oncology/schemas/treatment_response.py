
from typing import List 
from pydantic import Field
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import treatment_response as orm

class TreatmentResponseCreate(BaseSchema):
    
    __orm_model__ = orm.TreatmentResponse 
    
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
        description="Indicates the case of the patient who's treatment response is asseessed",
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Clinically-relevant date of the treatment response assessment',
        title='Assessment date',
    )
    recist: CodedConcept = Field(
        ...,
        description='The classification of the treatment response according to RECIST',
        title='RECIST',
        json_schema_extra={'x-terminology': 'CancerTreatmentResponse'},
    )
    recistInterpreted: Nullable[bool] = Field(
        None,
        description='Indicates whether the RECIST value was interpreted or taken from the radiology report',
        title='RECIST Interpreted?',
    )
    methodology: CodedConcept = Field(
        ...,
        description='Method used to assess and classify the treatment response',
        title='Assessment method',
        json_schema_extra={'x-terminology': 'CancerTreatmentResponseObservationMethod'},
    )
    assessedEntitiesIds: Nullable[List[UUID]] = Field(
        None,
        description='References to the neoplastic entities that were assesed for treatment response',
        title='Assessed neoplastic entities',
    )
    assessedBodysites: Nullable[List[CodedConcept]] = Field(
        None,
        description='Anatomical location assessed to determine the treatment response',
        title='Assessed anatomical location',
        json_schema_extra={'x-terminology': 'ObservationBodySite'},
    )


class TreatmentResponse(TreatmentResponseCreate, MetadataAnonymizationMixin):

    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"