from datetime import date, datetime
from typing import Literal, Union

from ninja import Schema
from pop.core.anonymization import (
    REDACTED_STRING,
    AnonymizationConfig,
    anonymize_by_redacting_string,
    anonymize_personal_date,
)
from pop.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from pop.core.types import Age, AgeBin, Array, Nullable
from pop.oncology import models as orm
from pydantic import AliasChoices, Field, field_validator


class PatientCaseSchema(ModelGetSchema):
    age: Union[int, Age, AgeBin] = Field(
        title="Age", alias="age", description="Approximate age of the patient in years"
    )
    dateOfBirth: Union[date, Literal[REDACTED_STRING]] = Field(  # type: ignore
        title="Date of birth",
        alias="date_of_birth",
        description="Date of birth of the patient",
        validation_alias=AliasChoices("dateOfBirth", "date_of_birth"),
    )
    overallSurvival: Nullable[float] = Field(
        None,
        title="Overall survival",
        alias="overall_survival",
        description="Overall survival of the patient since diagnosis",
        validation_alias=AliasChoices("overallSurvival", "overall_survival"),
    )
    ageAtDiagnosis: Nullable[Union[int, Age, AgeBin]] = Field(
        None,
        title="Age at diagnosis",
        description="Approximate age of the patient in years at the time of the initial diagnosis",
        alias="age_at_diagnosis",
        validation_alias=AliasChoices("ageAtDiagnosis", "age_at_diagnosis"),
    )
    dataCompletionRate: float = Field(
        title="Data completion rate",
        description="Percentage indicating the completeness of a case in terms of its data.",
        alias="data_completion_rate",
        validation_alias=AliasChoices("dataCompletionRate", "data_completion_rate"),
    )
    contributors: Union[list[str], Array[str]] = Field(
        title="Data contributors",
        description="Users that have contributed to the case by adding, updating or deleting data. Sorted by number of contributions in descending order.",
    )
    config = SchemaConfig(
        model=orm.PatientCase,
        anonymization=AnonymizationConfig(
            fields=["clinicalIdentifier", "clinicalCenter", "age", "ageAtDiagnosis"],
            key="id",
            functions={
                "dateOfBirth": anonymize_by_redacting_string,
                "dateOfDeath": anonymize_personal_date,
            },
        ),
    )

    @field_validator("age", "ageAtDiagnosis", mode="before")
    @classmethod
    def age_type_conversion(cls, value: Union[int, Age, AgeBin]) -> Age:
        if isinstance(value, int):
            return Age(value)
        else:
            return value


class PatientCaseCreateSchema(ModelCreateSchema):
    config = SchemaConfig(
        model=orm.PatientCase, exclude=("pseudoidentifier", "is_deceased")
    )


class PatientCaseDataCompletionStatusSchema(Schema):
    status: bool = Field(
        title="Status",
        description="Boolean indicating whether the data category has been marked as completed"
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
