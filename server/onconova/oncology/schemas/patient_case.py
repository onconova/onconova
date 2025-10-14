from datetime import date, datetime
from typing import Literal, Union

from ninja import Schema
from pydantic import Field, field_validator, model_validator

from onconova.core.anonymization import (
    REDACTED_STRING,
    anonymize_by_redacting_string,
    anonymize_personal_date,
)
from onconova.oncology import models as orm
from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept
from onconova.core.types import Age, AgeBin, Contributors, Nullable
from onconova.oncology.models.patient_case import PatientCaseConsentStatusChoices, PatientCaseVitalStatusChoices


class PatientCaseCreate(BaseSchema):
    
    __orm_model__ = orm.PatientCase
    
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
    clinicalCenter: str = Field(
        ...,
        description='Medical center where the patient data originally resides',
        title='Medical center',
        max_length=200,
    )
    clinicalIdentifier: str = Field(
        ...,
        description='Unique clinical identifier (typically the clinical information system identifier) unique for a physical patient',
        title='Clinical identifier',
        max_length=100,
    )
    consentStatus: PatientCaseConsentStatusChoices = Field(
        PatientCaseConsentStatusChoices.UNKNOWN,
        description='Status of the general consent by the patient for the use of their data for research purposes',
        title='Consent status',
    )
    gender: CodedConcept = Field(
        ...,
        description='Gender of the patient for legal/administrative purposes',
        title='Gender',
        json_schema_extra={'x-terminology': 'AdministrativeGender'}
    )
    race: Nullable[CodedConcept] = Field(
        None, 
        description='Race of the patient', 
        title='Race',        
        json_schema_extra={'x-terminology': 'Race'},
    )
    sexAtBirth: Nullable[CodedConcept] = Field(
        None, 
        description='Sex assigned at birth', 
        title='Birth sex',
        json_schema_extra={'x-terminology': 'BirthSex'},
    )
    genderIdentity: Nullable[CodedConcept] = Field(
        None,
        description="The patient's innate sense of their gender as reported",
        title='Gender identity',
        json_schema_extra={'x-terminology': 'GenderIdentity'},
    )
    dateOfBirth: date = Field(
        ...,
        description='Anonymized date of birth (year/month). The day is set to the first day of the month by convention.',
        title='Date of birth',
    )
    vitalStatus: PatientCaseVitalStatusChoices = Field(
        PatientCaseVitalStatusChoices.UNKNOWN,
        description='Whether the patient is known to be alive or decaeased or is unknkown.',
        title='Vital status',
    )
    dateOfDeath: Nullable[date] = Field(
        None,
        description='Anonymized date of death (year/month). The day is set to the first day of the month by convention.',
        title='Date of death',
    )
    causeOfDeath: Nullable[CodedConcept] = Field(
        None,
        description='Classification of the cause of death.',
        title='Cause of death',
        json_schema_extra={'x-terminology': 'CauseOfDeath'},
    )
    endOfRecords: Nullable[date] = Field(
        None,
        description='Date of the last known record about the patient if lost to followup or vital status is unknown.',
        title='End of records',
    )



class PatientCase(PatientCaseCreate, MetadataAnonymizationMixin):
        
    pseudoidentifier: str = Field(
        ..., 
        description='Pseudoidentifier of the patient', 
        title='Pseudoidentifier',
        max_length=40,
    )
    age: Union[Age, AgeBin] = Field(
        title="Age", 
        description="Approximate age of the patient in years"
    )
    dateOfBirth: Union[date, Literal[REDACTED_STRING]] = Field(  # type: ignore
        title="Date of birth",
        description="Date of birth of the patient",
    )
    overallSurvival: Nullable[float] = Field(
        None,
        title="Overall survival",
        description="Overall survival of the patient since diagnosis",
    )
    ageAtDiagnosis: Nullable[Union[int, Age, AgeBin]] = Field(
        None,
        title="Age at diagnosis",
        description="Approximate age of the patient in years at the time of the initial diagnosis",
    )
    dataCompletionRate: float = Field(
        title="Data completion rate",
        description="Percentage indicating the completeness of a case in terms of its data.",
    )
    contributors: Contributors = Field(
        title="Data contributors",
        description="Users that have contributed to the case by adding, updating or deleting data. Sorted by number of contributions in descending order.",
    )
    
    __anonymization_fields__ = ("dateOfBirth", "dateOfDeath", "clinicalIdentifier", "clinicalCenter", "age", "ageAtDiagnosis")
    __anonymization_key__ = "id"
    __anonymization_functions__ = {
        "dateOfBirth": anonymize_by_redacting_string,
        "dateOfDeath": anonymize_personal_date,
    }
    

    @field_validator("age", "ageAtDiagnosis", mode="before")
    @classmethod
    def age_type_conversion(cls, value: int | Age | AgeBin) -> Age | AgeBin:
        if isinstance(value, int):
            return Age(value)
        return value

    @model_validator(mode="after")
    @classmethod
    def validate_vital_status_scenarios(cls, obj):
        if obj.vitalStatus == PatientCaseVitalStatusChoices.ALIVE:
            if obj.dateOfDeath:
                raise ValueError("An alive patient cannot have a date of death")
            if obj.causeOfDeath:
                raise ValueError("An alive patient cannot have a cause of death")
            if obj.endOfRecords:
                raise ValueError(
                    "If patient is known to be alive, it cannot have an end of records."
                )
        if obj.vitalStatus == PatientCaseVitalStatusChoices.UNKNOWN:
            if obj.dateOfDeath:
                raise ValueError(
                    "An unkonwn vital status patient cannot have a date of death"
                )
            if obj.causeOfDeath:
                raise ValueError(
                    "An unkonwn vital status patient cannot have a cause of death"
                )
            if not obj.endOfRecords:
                raise ValueError(
                    "If patient vital status is unknown, it must have a valid end of records date."
                )
        if obj.vitalStatus == PatientCaseVitalStatusChoices.DECEASED:
            if not obj.dateOfDeath:
                raise ValueError("A deceased patient must have a date of death")
            if obj.endOfRecords:
                raise ValueError(
                    "If patient is known to be deceased, it cannot have an end of records."
                )
        return obj



class PatientCaseDataCompletionStatus(Schema):
    status: bool = Field(
        title="Status",
        description="Boolean indicating whether the data category has been marked as completed",
    )
    username: Nullable[str] = Field(
        title="Username",
        default=None,
        description="Username of the person who marked the category as completed",
    )
    timestamp: Nullable[datetime] = Field(
        default=None,
        title="Timestamp",
        description="Username of the person who marked the category as completed",
    )
