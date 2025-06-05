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
    contributors: Optional[list[str]] = Field(
        title='Data contributors',
        description='Users that have contributed to the case by adding, updating or deleting data. Sorted by number of contributions in descending order.', 
    ) 
    config = SchemaConfig(model = orm.PatientCase)

    @staticmethod
    def resolve_clinicalIdentifier(obj, context) -> str:
        if isinstance(obj, dict):
            return obj.get('clinicalIdentifier')
        elif isinstance(obj, Schema):   
            return obj.clinicalIdentifier
        if not context:
            return obj.clinical_identifier
        request = context["request"]
        if request.user.is_authenticated and request.user.can_access_sensitive_data:
            return obj.clinical_identifier
        return '*************'


class PatientCaseCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model = orm.PatientCase, exclude=('pseudoidentifier','is_deceased'))


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

    