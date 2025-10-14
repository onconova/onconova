from pydantic import Field
from datetime import date as date_aliased 

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, Measure
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import vitals as orm



class VitalsCreate(BaseSchema):

    __orm_model__ = orm.Vitals
    
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
        description="Indicates the case of the patient who's vitals are assesed",
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Clinically-relevant date at which the vitals were recorded.',
        title='Assessment date',
    )
    height: Nullable[Measure] = Field(
        None,
        description='Height of the patient',
        title='Height',
        json_schema_extra={
            "x-measure": "Distance",
            "x-default-unit": "m"
        },
    )
    weight: Nullable[Measure] = Field(
        None,
        description='Weight of the patient',
        title='Weight',
        json_schema_extra={
            "x-measure": "Mass",
            "x-default-unit": "kg"
        },
    )
    bloodPressureSystolic: Nullable[Measure] = Field(
        None,
        description='Systolic blood pressure of the patient',
        title='Systolic blood pressure',
        json_schema_extra={
            "x-measure": "Pressure",
            "x-default-unit": "mmHg"
        },
    )
    bloodPressureDiastolic: Nullable[Measure] = Field(
        None,
        description='Diastolic blood pressure of the patient',
        title='Diastolic blood pressure',
        json_schema_extra={
            "x-measure": "Pressure",
            "x-default-unit": "mmHg"
        },
    )
    temperature: Nullable[Measure] = Field(
        None,
        description='Temperature of the patient',
        title='Temperature',
        json_schema_extra={
            "x-measure": "Temperature",
            "x-default-unit": "celsius"
        },
    )


class Vitals(VitalsCreate, MetadataAnonymizationMixin):

    bodyMassIndex: Nullable[Measure] = Field(
        None,
        title="Body mass index",
        description="Bodymass index of the patient",
        json_schema_extra={
            "x-measure": "MassPerArea"
        },
    )
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"