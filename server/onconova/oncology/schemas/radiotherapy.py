from typing import List
from pydantic import Field

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, MetadataMixin, CodedConcept, Measure, Period
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import radiotherapy as orm


class RadiotherapyDosageCreate(BaseSchema):
    
    __orm_model__ = orm.RadiotherapyDosage
    
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
    fractions: Nullable[int] = Field(
        None,
        description='The total number of radiotherapy fractions delivered over the treatment period.',
        title='Total fractions',
    )
    dose: Nullable[Measure] = Field(
        None,
        description='Total radiation dose delivered over the full radiotherapy course',
        title='Total radiation dose',
        json_schema_extra={
            'x-default-unit': 'Gy',
            'x-measure': 'RadiationDose',
        },
    )
    irradiatedVolume: CodedConcept = Field(
        ...,
        description='Anatomical location of the irradiated volume',
        title='Irradiated volume',
        json_schema_extra={'x-terminology': 'RadiotherapyTreatmentLocation'},
    )
    irradiatedVolumeMorphology: Nullable[CodedConcept] = Field(
        None,
        description='Morphology of the anatomical location of the irradiated volume',
        title='Irradiated volume morphology',
        json_schema_extra={'x-terminology': 'RadiotherapyVolumeType'},
    )
    irradiatedVolumeQualifier: Nullable[CodedConcept] = Field(
        None,
        description='General qualifier for the anatomical location of the irradiated volume',
        title='Irradiated volume qualifier',
        json_schema_extra={'x-terminology': 'RadiotherapyTreatmentLocationQualifier'},
    )


class RadiotherapyDosage(RadiotherapyDosageCreate, MetadataMixin):
    pass


class RadiotherapySettingCreate(BaseSchema):
    
    __orm_model__ = orm.RadiotherapySetting 
    
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
    modality: CodedConcept = Field(
        ...,
        description='Modality of external beam or brachytherapy radiation procedures',
        title='Modality',
        json_schema_extra={'x-terminology': 'RadiotherapyModality'},
    )
    technique: CodedConcept = Field(
        ...,
        description='Technique of external beam or brachytherapy radiation procedures',
        title='Technique',
        json_schema_extra={'x-terminology': 'RadiotherapyTechnique'},
    )

class RadiotherapySetting(RadiotherapySettingCreate, MetadataMixin):
    pass



class RadiotherapyCreate(BaseSchema):
    
    __orm_model__ = orm.Radiotherapy 
    
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
        description='Indicates the case of the patient who received the radiotherapy',
        title='Patient case',
    )
    period: Period = Field(
        ...,
        description='Clinically-relevant period during which the radiotherapy was administered to the patient.',
        title='Treatment period',
    )
    sessions: int = Field(
        ...,
        description='The total number of radiotherapy sessions over the treatment period.',
        title='Total sessions',
    )
    intent: orm.RadiotherapyIntentChoices = Field(
        ...,
        description='Treatment intent of the system therapy',
        title='Intent',
    )
    terminationReason: Nullable[CodedConcept] = Field(
        None,
        description='Explanation for the premature or planned termination of the radiotherapy',
        title='Termination reason',
        json_schema_extra={'x-terminology': 'TreatmentTerminationReason'},
    )
    therapyLineId: Nullable[UUID] = Field(
        None,
        description='Therapy line to which the radiotherapy is assigned to',
        title='Therapy line',
    )
    targetedEntitiesIds: Nullable[List[UUID]] = Field(
        None,
        description='References to the neoplastic entities that were targeted by the radiotherapy',
        title='Targeted neoplastic entities',
    )
    

class Radiotherapy(RadiotherapyCreate, MetadataAnonymizationMixin):
    
    duration: Measure = Field(
        title="Duration",
        description="Duration of treatment",
        json_schema_extra={"x-measure": "Time"},
    )
    dosages: List[RadiotherapyDosage] = Field(
        title="Dosages",
        description="Radiation doses administered during the radiotherapy",
    )
    settings: List[RadiotherapySetting] = Field(
        title="Settings",
        description="Settings of the radiotherapy irradiation procedure",
    )

    __anonymization_fields__ = ("period",)
    __anonymization_key__ = "caseId"
