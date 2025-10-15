from typing import List
from pydantic import Field

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, MetadataMixin, Period, Measure, CodedConcept
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import systemic_therapy as orm

class SystemicTherapyMedicationCreate(BaseSchema):
    
    __orm_model__ = orm.SystemicTherapyMedication 
    
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
    drug: CodedConcept = Field(
        ...,
        description='Antineoplastic drug/medication administered to the patient',
        title='Antineoplastic Drug',
        json_schema_extra={'x-terminology': 'AntineoplasticAgent'},
    )
    route: Nullable[CodedConcept] = Field(
        None,
        description='Drug administration route',
        title='Route',
        json_schema_extra={'x-terminology': 'DosageRoute'},
    )
    usedOfflabel: Nullable[bool] = Field(
        None,
        description='Indicates whether a medication was used off-label at the time of administration',
        title='Off-label use',
    )
    withinSoc: Nullable[bool] = Field(
        None,
        description='Indicates whether a medication was within standard of care (SOC) at the time of administration.',
        title='Within SOC',
    )
    dosageMassConcentration: Nullable[Measure] = Field(
        None,
        description='Dosage of the medication expressed in mass concentration (if revelant/appliccable)',
        title='Dosage - Mass concentration',
        json_schema_extra={
            'x-measure': 'MassConcentration',
            'x-default-unit': 'g/l',
        },
    )
    dosageMass: Nullable[Measure] = Field(
        None,
        description='Dosage of the medication expressed in a fixed mass (if revelant/appliccable)',
        title='Dosage - Fixed Mass',
        json_schema_extra={
            'x-measure': 'Mass',
            'x-default-unit': 'g',
        },
    )
    dosageVolume: Nullable[Measure] = Field(
        None,
        description='Dosage of the medication expressed in a volume (if revelant/appliccable)',
        title='Dosage - Volume',
        json_schema_extra={
            'x-measure': 'Volume',
            'x-default-unit': 'l',
        },
    )
    dosageMassSurface: Nullable[Measure] = Field(
        None,
        description='Dosage of the medication expressed in a mass per body surface area (if revelant/appliccable)',
        title='Dosage - Mass per body surface',
        json_schema_extra={
            'x-measure': 'MassPerArea',
            'x-default-unit': 'g/square_meter',
        },
    )
    dosageRateMassConcentration: Nullable[Measure] = Field(
        None,
        description='Dosage rate of the medication expressed in mass concentration (if revelant/appliccable)',
        title='Dosage rate - Mass concentration',
        json_schema_extra={
            'x-measure': 'MassConcentrationPerTime',
            'x-default-unit': 'g/l/s',
        },
    )
    dosageRateMass: Nullable[Measure] = Field(
        None,
        description='Dosage rate of the medication expressed in a fixed mass (if revelant/appliccable)',
        title='Dosage rate - Fixed Mass',
        json_schema_extra={
            'x-measure': 'MassPerTime',
            'x-default-unit': 'g/s',
        },
    )
    dosageRateVolume: Nullable[Measure] = Field(
        None,
        description='Dosage rate of the medication expressed in a volume (if revelant/appliccable)',
        title='Dosage rate - Volume',
        json_schema_extra={
            'x-measure': 'VolumePerTime',
            'x-default-unit': 'l/s',
        },
    )
    dosageRateMassSurface: Nullable[Measure] = Field(
        None,
        description='Dosage rate of the medication expressed in a mass per body surface area (if revelant/appliccable)',
        title='Dosage rate - Mass per body surface',
        json_schema_extra={
            'x-measure': 'MassPerAreaPerTime',
            'x-default-unit': 'g/square_meter/s',
        },
    )


class SystemicTherapyMedication(SystemicTherapyMedicationCreate, MetadataMixin):
    pass



class SystemicTherapyCreate(BaseSchema):
    
    __orm_model__ = orm.SystemicTherapy 
    
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
        description='Indicates the case of the patient who received the systemic therapy',
        title='Patient case',
    )
    period: Period = Field(
        ...,
        description='Clinically-relevant period during which the therapy was administered to the patient.',
        title='Treatment period',
    )
    cycles: Nullable[int] = Field(
        None,
        description='The total number of treatment cycles during the treatment period.',
        title='Cycles',
    )
    intent: orm.SystemicTherapyIntentChoices = Field(
        ...,
        description='Treatment intent of the system therapy',
        title='Intent',
    )
    adjunctiveRole: Nullable[CodedConcept] = Field(
        None,
        description='Indicates the role of the adjunctive therapy (if applicable).',
        title='Treatment Role',
        json_schema_extra={'x-terminology': 'AdjunctiveTherapyRole'},
    )
    terminationReason: Nullable[CodedConcept] = Field(
        None,
        description='Explanation for the premature or planned termination of the systemic therapy',
        title='Termination reason',
        json_schema_extra={'x-terminology': 'TreatmentTerminationReason'},
    )
    therapyLineId: Nullable[UUID] = Field(
        None,
        description='Therapy line to which the systemic therapy is assigned to',
        title='Therapy line',
    )
    targetedEntitiesIds: Nullable[List[UUID]] = Field(
        None,
        description='References to the neoplastic entities that were targeted by the systemic therapy',
        title='Targeted neoplastic entities',
    )


class SystemicTherapy(SystemicTherapyCreate, MetadataAnonymizationMixin):
    
    medications: List[SystemicTherapyMedication] = Field(
        title="Medications",
        description="Medications administered during the systemic therapy",
    )
    isAdjunctive: bool = Field(
        ...,
        description='Indicates whether it is adjunctive therapy instead of a primary therapy',
        title='Treatment Role',
    )
    duration: Measure = Field(
        title="Duration",
        description="Duration of treatment",
        json_schema_extra={
            "x-measure": "Time", 
            "x-default-unit": "day"
        },
    )

    __anonymization_fields__ = ("period",)
    __anonymization_key__ = "caseId"
