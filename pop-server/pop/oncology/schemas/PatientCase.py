from pop.oncology.models import PatientCase, PatientCaseDataCompletion
from django.db.models import Q
from datetime import datetime
from pop.core.schemas import ModelSchema, ModelFilterSchema, CREATE_IGNORED_FIELDS, create_filters_schema
from .NeoplasticEntity import NeoplasticEntitySchema, NeoplasticEntityCreateSchema
from ninja import Schema
from pydantic import Field, AliasChoices
from typing import Optional, List

class PatientCaseDataCompletionStatusSchema(Schema):
    status: bool = Field(description='Boolean indicating whether the data category has been marked as completed')
    username: Optional[str] = Field(None,description='Username of the person who marked the category as completed')
    timestamp: Optional[datetime] = Field(None,description='Username of the person who marked the category as completed')

class PatientCaseSchema(ModelSchema):
    age: int = Field(title='Age', alias='db_age', description='Approximate age of the patient in years', json_schema_extra={'django_field': 'db_age'}) 
    dataCompletionRate: float = Field(
        title='Data completion rate',
        description='Percentage indicating the completeness of a case in terms of its data.', 
        alias='db_data_completion_rate',
        validation_alias=AliasChoices('dataCompletionRate', 'data_completion_rate'),
    ) 

    class Meta:
        name = 'PatientCase'
        model = PatientCase
        fields = '__all__'

class PatientCaseCreateSchema(ModelSchema):
    class Meta:
        name = 'PatientCaseCreate'
        model = PatientCase
        exclude = (
            *CREATE_IGNORED_FIELDS,
            'pseudoidentifier', 
            'is_deceased',
        )

PatientCaseFiltersBase = create_filters_schema(
    schema = PatientCaseSchema, 
    name='PatientCaseFilters'
)

class PatientCaseFilters(PatientCaseFiltersBase):
    manager: Optional[str] = Field(None, description='Filter for a particular case manager by its username')

    def filter_manager(self, value: str) -> Q:
        return Q(created_by__username=self.manager) if value is not None else Q()




class PatientCaseBundleSchema(ModelSchema):
    age: int = Field(description='Approximate age of the patient in years') 
    neoplasticEntities: List[NeoplasticEntitySchema] = Field(None,description='Neoplastic entities') 

    class Meta:
        name = 'PatientCaseBundle'
        model = PatientCase
        fields = '__all__'

class PatientCaseBundleCreateSchema(ModelSchema):    
    neoplasticEntities: List[NeoplasticEntityCreateSchema] = Field(description='Neoplastic entities') 

    class Meta:
        name = 'PatientCaseBundleCreate'
        model = PatientCase
        exclude = (
            *CREATE_IGNORED_FIELDS,
            'is_deceased',
        )
    