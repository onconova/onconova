from typing import List
from pydantic import Field
from uuid import UUID
from datetime import date as date_aliased
from ninja import Schema
from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept
from onconova.core.types import Nullable
from onconova.oncology.models import comorbidities as orm


class ComorbiditiesAssessmentCreate(BaseSchema):
    
    __orm_model__ = orm.ComorbiditiesAssessment
    
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
        description="Indicates the case of the patient who's comorbidities are being recorded",
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description="Clinically-relevant date at which the patient's comorbidities were assessed and recorded.",
        title='Assessment date',
    )
    indexConditionId: UUID = Field(
        ...,
        description='The primary neoplastic entity against which comorbidities are assessed',
        title='Index neoplastic entity',
    )
    panel: Nullable[orm.ComorbiditiesAssessmentPanelChoices] = Field(
        None, 
        description='Comorbidities panel', 
        title='Panel',
    )
    presentConditions: Nullable[List[CodedConcept]] = Field(
        None,
        description='Present comorbid conditions',
        title='Present comorbid conditions',
        json_schema_extra={'x-terminology': 'ICD10Condition'},
    )
    absentConditions: Nullable[List[CodedConcept]] = Field(
        None,
        description='Absent comorbid conditions',
        title='Absent comorbid conditions',
        json_schema_extra={'x-terminology': 'ICD10Condition'},
    )
        
class ComorbiditiesAssessment(ComorbiditiesAssessmentCreate, MetadataAnonymizationMixin):
    
    score: Nullable[int | float] = Field(
        default=None,
        title="Score",
        description="Comorbidity score",
        alias="score",
    )

    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    

class ComorbidityPanelCategory(Schema):
    label: str = Field(
        title="Label", 
        description="Label of the comorbidity panel category"
    )
    default: Nullable[CodedConcept] = Field(
        default=None, title="Default", 
        description="Default choice for category",
        json_schema_extra={'x-terminology': 'ICD10Condition'},
    )
    conditions: List[CodedConcept] = Field(
        title="Conditions",
        description="List of conditions included in the panel category",
        json_schema_extra={'x-terminology': 'ICD10Condition'},
    )


class ComorbiditiesPanel(Schema):
    name: str = Field(
        title="Name", 
        description="Comorbidity panel name"
    )
    categories: List[ComorbidityPanelCategory] = Field(
        title="Categories", 
        description="Comorbidity panel categories",
    )
