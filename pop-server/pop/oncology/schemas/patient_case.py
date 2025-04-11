from datetime import datetime
from typing import Optional
from pydantic import Field, AliasChoices
from ninja import Schema
from django.db.models import Q

from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig, create_filters_schema

class PatientCaseSchema(ModelGetSchema):
    age: int = Field(
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
    ageAtDiagnosis: Optional[int] = Field(
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
    config = SchemaConfig(model = orm.PatientCase)


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

    