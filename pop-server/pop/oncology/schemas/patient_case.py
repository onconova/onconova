from datetime import datetime
from typing import Optional, Union
from enum import Enum
from pydantic import Field, AliasChoices, field_validator
from ninja import Schema
from django.db.models import Q

from pop.oncology import models as orm
from pop.core.types import Age, AgeBin
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig, create_filters_schema
from pop.core.schemas.factory.fields import POPTypeAnnotations
from pop.core.anonymization import AnonymizationConfig, anonymize_personal_date, model_validator

class PatientCaseSchema(ModelGetSchema):
    age: Union[int, Age, AgeBin] = Field(
        title='Age', 
        alias='age', 
        description='Approximate age of the patient in years'
    ) 
    overallSurvival: Optional[float] = Field(
        None,
        title='Overall survival', 
        alias='overall_survival', 
        description='Overall survival of the patient since diagnosis',
        validation_alias=AliasChoices('overallSurvival','overall_survival'),
    ) 
    ageAtDiagnosis: Optional[ Union[int, Age, AgeBin]] = Field(
        None,
        title='Age at diagnosis', 
        description='Approximate age of the patient in years at the time of the initial diagnosis',
        alias='age_at_diagnosis', 
        validation_alias=AliasChoices('ageAtDiagnosis','age_at_diagnosis'),
    ) 
    dataCompletionRate: float = Field(
        title='Data completion rate',
        description='Percentage indicating the completeness of a case in terms of its data.', 
        alias='data_completion_rate',
        validation_alias=AliasChoices('dataCompletionRate', 'data_completion_rate'),
    ) 
    config = SchemaConfig(model = orm.PatientCase, anonymization=AnonymizationConfig(fields=['clinicalIdentifier', 'clinicalCenter','age','ageAtDiagnosis'], key='id'))

    @model_validator(mode='after')
    @classmethod
    def personal_dates_anonymization(cls, obj):
        if getattr(obj,'anonymize', None):
            if obj.dateOfBirth:
                date_of_birth_year = anonymize_personal_date(obj.dateOfBirth)
                obj.dateOfBirth = datetime(date_of_birth_year,1,1).date()
            if obj.dateOfDeath:
                date_of_death_year = anonymize_personal_date(obj.dateOfDeath)
                obj.dateOfDeath = datetime(date_of_death_year,1,1).date()
        return obj         
    
    
    @field_validator('age', 'ageAtDiagnosis', mode='before')
    @classmethod
    def age_type_conversion(cls, value: Union[int, Age, AgeBin]) -> Age:
        if isinstance(value, int):
            return Age(value)
        else:
            return value


class PatientCaseCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model = orm.PatientCase, exclude=('pseudoidentifier','is_deceased'))

PatientCaseFiltersBase = create_filters_schema(
    schema = PatientCaseSchema, 
    name='PatientCaseFilters'
)

class PatientCaseFilters(PatientCaseFiltersBase):
    manager: Optional[str] = Field(None, description='Filter for a particular case manager by its username')

    def filter_manager(self, value: str) -> Q:
        return Q(created_by=self.manager) if value is not None else Q()


class PatientCaseDataCompletionStatusSchema(Schema):
    status: bool = Field(
        description='Boolean indicating whether the data category has been marked as completed'
    )
    username: Optional[str] = Field(
        default=None,
        description='Username of the person who marked the category as completed'
    )
    timestamp: Optional[datetime] = Field(
        default=None, description='Username of the person who marked the category as completed'
    )

    