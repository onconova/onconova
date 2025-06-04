from ninja import Schema, Field
from typing import Tuple, Optional,  Union, Any, List, Dict, Type, get_args
from enum import Enum 
from django.db.models import Q
from pydantic import BaseModel, AliasChoices, Field, create_model, ConfigDict, field_validator, AliasPath, BaseModel as PydanticBaseModel
from pop.core.utils import is_optional, _get_deepest_args, is_union, is_list
from pop.core.schemas import CodedConceptSchema, PeriodSchema, RangeSchema
from pop.core import transforms as tfs
from pop.oncology import schemas as oncology_schemas
import pop.oncology.schemas as sc
from pop.analytics import models as orm
from pop.core.schemas.factory import create_filters_schema, BaseSchema
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

DataResource = Enum('DataResource', {
    model.__name__.upper(): model.__name__ for model in oncology_schemas.ONCOLOGY_SCHEMAS if issubclass(model, ModelGetSchema) and model.__name__ not in ['GenomicSignature']
}, type=str)

class DatasetRule(Schema):
    resource: DataResource # type: ignore
    field: str
    transform: Optional[Union[str, Tuple[str, Any]]] = None   


class Dataset(ModelGetSchema):
    rules: List[DatasetRule] = Field([], description='Composition rules of the dataset')
    config = SchemaConfig(model=orm.Dataset)
    
class DatasetCreate(ModelCreateSchema):
    rules: List[DatasetRule] = Field([], description='Composition rules of the dataset')
    config = SchemaConfig(model=orm.Dataset)
    
DatasetFiltersBase = create_filters_schema(
    schema = Dataset, 
    name='DatasetFilters'
)

class DatasetFilters(DatasetFiltersBase):
    createdBy: Optional[str] = Field(None, description='Filter for a particular cohort creator by its username')

    def filter_createdBy(self, value: str) -> Q:
        return Q(created_by=self.createdBy) if value is not None else Q()



def create_partial_schema(schema: Type[Schema]) -> Type[Schema]:
    """
    Given a Pydantic model class, return a new model class with the same fields and validators,
    but all fields are optional (default=None).
    """
    # Prepare new fields dict, ensure they all are anonymized
    new_fields = {}

    for field_name, model_field in schema.model_fields.items():
        if field_name in ['anonymized']:
            continue
        
            
        # Get schema field annotation 
        annotation = model_field.annotation

        if field_name == 'ageAtDiagnosis':
            print(field_name, annotation)
        if is_optional(annotation):
            annotation = get_args(annotation)
            if len(annotation) > 1:
                annotation = Union[annotation]
            else:
                annotation = get_args(annotation)[0]

        if field_name == 'ageAtDiagnosis':
            print(field_name, annotation)
        if is_list(annotation):
            list_annotation = get_args(annotation)[0]
            if issubclass(list_annotation, PydanticBaseModel) and not issubclass(list_annotation, CodedConceptSchema):
                related_schema_partial = create_partial_schema(list_annotation)
                annotation = List[related_schema_partial]        
                
        if issubclass(annotation, PydanticBaseModel) and not issubclass(annotation, CodedConceptSchema):
                annotation = create_partial_schema(annotation)
        
        # Set default to None
        if 'CodedConcept' in str(annotation):
            transforms = [tfs.GetCodedConceptDisplay, tfs.GetCodedConceptCode, tfs.GetCodedConceptSystem]
            new_fields[field_name] = (Optional[Union[str, List[Optional[str]]]], Field(default=None, validation_alias=AliasChoices(*[f'{model_field.alias}.{transform.name}' for transform in transforms])))
        elif 'Measure' in str(annotation):
            new_fields[field_name] = (Optional[float], Field(default=None, validation_alias=model_field.validation_alias))
        elif 'Period' in str(annotation):
            new_fields[field_name] = (Optional[str], Field(default=None, validation_alias=model_field.validation_alias))
        else:
            new_fields[field_name] = (Optional[annotation], Field(default=None, validation_alias=model_field.validation_alias))
    
    validators = None
    if 'anonymized' in schema.model_fields:
        validators = {
            'always_anonymized': field_validator('anonymized')(lambda cls,v: True),
        }
    
    # Create a new model dynamically with the modified fields
    partial_schema = create_model(
        schema.__name__ + "Partial",
        __base__ = schema,
        __validators__ = validators,
        __config__ = ConfigDict(
            from_attributes=True,
            populate_by_name = True,
            arbitrary_types_allowed = True,
            exclude_unset = True,
        ),
        **new_fields,
    )
    
    
    return partial_schema
    

partial_schemas = {
    schema.__name__: create_partial_schema(schema) for schema in oncology_schemas.ONCOLOGY_SCHEMAS if issubclass(schema, ModelGetSchema)   
}


class PatientCaseDataset(partial_schemas['PatientCase']):
        
    pseudoidentifier: str = Field(title='Pseudoidentifier')
    neoplasticEntities: Optional[List[partial_schemas['NeoplasticEntity']]] = Field(
        default=None, validation_alias=AliasChoices('neoplasticEntities','neoplastic_entities_resources')
    ) 
    tnmStagings: Optional[List[partial_schemas['TNMStaging']]] = Field(
         default=None, validation_alias=AliasChoices('tnmStagings','tnm_stagings_resources')
    )
    figoStagings: Optional[List[partial_schemas['TNMStaging']]] = Field(
         default=None, validation_alias=AliasChoices('figoStagings','figo_stagings_resources')
    )
    tumorMarkers: Optional[List[partial_schemas['TumorMarker']]] = Field(
         default=None, validation_alias=AliasChoices('tumorMarkers','tumor_markers_resources')
    )  
    riskAssessments: Optional[List[partial_schemas['RiskAssessment']]] = Field(
         default=None, validation_alias=AliasChoices('riskAssessments','risk_assessments_resources')
    )  
    therapyLines: Optional[List[partial_schemas['TherapyLine']]] = Field(
         default=None, validation_alias=AliasChoices('therapyLines','therapy_lines_resources')
    )  
    systemicTherapies: Optional[List[partial_schemas['SystemicTherapy']]] = Field(
         default=None, validation_alias=AliasChoices('systemicTherapies','systemic_therapies_resources')
    )  
    surgeries: Optional[List[partial_schemas['Surgery']]] = Field(
         default=None, validation_alias=AliasChoices('surgeries','surgeries_resources')
    )  
    radiotherapies: Optional[List[partial_schemas['Radiotherapy']]] = Field(
         default=None, validation_alias=AliasChoices('radiotherapies','radiotherapies_resources'),
    )  
    adverseEvents: Optional[List[partial_schemas['AdverseEvent']]] = Field(
         default=None, validation_alias=AliasChoices('adverseEvents','adverse_events_resources')
    )  
    treatmentResponses: Optional[List[partial_schemas['TreatmentResponse']]] = Field(
         default=None, validation_alias=AliasChoices('treatmentResponses','treatment_responses_resources')
    )  
    performanceStatus: Optional[List[partial_schemas['PerformanceStatus']]] = Field(
         default=None, validation_alias=AliasChoices('performanceStatus','performance_status_resources')
    )  
    comorbidities: Optional[List[partial_schemas['ComorbiditiesAssessment']]] = Field(
         default=None, validation_alias=AliasChoices('comorbidities','comorbidities_resources')
    )  
    genomicVariants: Optional[List[partial_schemas['GenomicVariant']]] = Field(
         default=None, validation_alias=AliasChoices('genomicVariants','genomic_variants_resources')
    )  
    genomicSignatures: Optional[List[Union[
        partial_schemas['TumorMutationalBurden'], partial_schemas['MicrosatelliteInstability'],
        partial_schemas['LossOfHeterozygosity'], partial_schemas['HomologousRecombinationDeficiency'],
        partial_schemas['TumorNeoantigenBurden'], partial_schemas['AneuploidScore']]]] = Field(
        default=None, 
    )  
    vitals: Optional[List[partial_schemas['Vitals']]] = Field(
         default=None, validation_alias=AliasChoices('vitals','vitals_resources')
    )    
    lifestyles: Optional[List[partial_schemas['Lifestyle']]] = Field(
         default=None, validation_alias=AliasChoices('lifestyles','lifestyles_resources')
    )  
    familyHistory: Optional[List[partial_schemas['FamilyHistory']]] =  Field(
         default=None, validation_alias=AliasChoices('familyHistory','family_histories_resources')
    )  
    vitals: Optional[List[partial_schemas['Vitals']]] = Field(
         default=None, validation_alias=AliasChoices('vitals','vitals_resources')
    )  
    unspecifiedTumorBoards: Optional[List[partial_schemas['UnspecifiedTumorBoard']]] = Field(
         default=None, validation_alias=AliasChoices('unspecifiedtumorboards','unspecified_tumor_boards_resources')
    )  
    molecularTumorBoards: Optional[List[partial_schemas['UnspecifiedTumorBoard']]] = Field(
         default=None, validation_alias=AliasChoices('molecularTumorBoards','molecular_tumor_boards_resources')
    )  
    