from datetime import date as date_aliased
from pydantic import Field
from uuid import UUID 
from typing import List

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept, Measure
from onconova.core.types import Nullable
from onconova.oncology import models as orm


class LifestyleCreate(BaseSchema):

    __orm_model__ = orm.Lifestyle
    
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
        description="Indicates the case of the patient who's lifestyle is assesed",
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description="Clinically-relevant date at which the patient's lifetyle was assessed and recorded.",
        title='Assessment date',
    )
    smokingStatus: Nullable[CodedConcept] = Field(
        None,
        description='Tobacco consumption status',
        title='Smoking Status',
        json_schema_extra={'x-terminology': 'SmokingStatus'},
    )
    smokingPackyears: Nullable[float] = Field(
        None,
        description='Smoking pack-years (if applicable)',
        title='Smoking packyears',
    )
    smokingQuited: Nullable[Measure] = Field(
        None,
        description='Estimated time since quitting smoking (if applicable)',
        title='Time since quitted smoking',
        json_schema_extra={
            'x-measure': 'Time',
            'x-default-unit': 'year',
        },
    )
    alcoholConsumption: Nullable[CodedConcept] = Field(
        None,
        description='Frequency of alcohol consumption',
        title='Alcohol consumption',
        json_schema_extra={'x-terminology': 'AlcoholConsumptionFrequency'},
    )
    nightSleep: Nullable[Measure] = Field(
        None,
        description='Estimated average sleep time per night',
        title='Night sleep',
        json_schema_extra={
            'x-measure': 'Time',
            'x-default-unit': 'hour',
        },
    )
    recreationalDrugs: Nullable[List[CodedConcept]] = Field(
        None,
        description='Any recreational drug(s) used by the patient',
        title='Recreational drugs',
        json_schema_extra={'x-terminology': 'RecreationalDrug'},
    )
    exposures: Nullable[List[CodedConcept]] = Field(
        None,
        description='Environmental or occupational exposures to hazards or carcinogenic agents',
        title='Exposures',
        json_schema_extra={'x-terminology': 'ExposureAgent'},
    )


class Lifestyle(LifestyleCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"