from typing import Tuple, Optional,  Union, Any, List, Type, get_args
from enum import Enum 

from django.db.models import Q

from ninja import Schema, Field
from pydantic import AliasChoices, Field, create_model, ConfigDict, field_validator, BaseModel as PydanticBaseModel

from pop.core.utils import is_optional, is_list
from pop.core.schemas import CodedConcept as CodedConceptSchema
from pop.core.serialization import transforms as tfs
from pop.core.serialization.factory import create_filters_schema
from pop.core.serialization.metaclasses import ModelGetSchema, ModelCreateSchema, SchemaConfig

from pop.oncology import schemas as oncology_schemas

from pop.research.models import dataset as orm



# Dynamically generate Enum from oncology schemas (excluding 'GenomicSignature')
DataResource = Enum(
    'DataResource',
    {
        model.__name__.upper(): model.__name__
        for model in oncology_schemas.ONCOLOGY_SCHEMAS
        if issubclass(model, ModelGetSchema) and model.__name__ != 'GenomicSignature'
    },
    type=str
)


class DatasetRule(Schema):
    """
    A rule defining how a dataset is composed from a specific resource and field.

    Attributes:
        resource (DataResource): The resource (model type) this rule applies to.
        field (str): Dot-separated path to the target field within the resource.
        transform (Optional[Union[str, Tuple[str, Any]]]): Optional transformation or expression to apply.
    """
    resource: DataResource = Field( # type: ignore
        title="Resource",
        description="The oncology resource this rule references."
    )  # type: ignore

    field: str = Field(
        title="Field",
        description="Dot-separated path of the field within the resource (e.g. 'medications.drug')."
    )

    transform: Optional[Union[str, Tuple[str, Any]]] = Field(
        default=None,
        title="Transform",
        description="Optional transform expression or mapping applied to the field's value."
    )


class Dataset(ModelGetSchema):
    """
    Schema for retrieving a dataset definition, including its composition rules.
    """
    rules: List[DatasetRule] = Field(
        default=[],
        title="Rules",
        description="List of composition rules that define the dataset's structure."
    )

    config = SchemaConfig(model=orm.Dataset)


class DatasetCreate(ModelCreateSchema):
    """
    Schema for creating a new dataset, including its composition rules.
    """
    rules: List[DatasetRule] = Field(
        default=[],
        title="Rules",
        description="List of composition rules that define the dataset's structure."
    )

    config = SchemaConfig(model=orm.Dataset)


# Base filters schema generated from the Dataset schema
DatasetFiltersBase = create_filters_schema(
    schema=Dataset,
    name="DatasetFilters"
)


class DatasetFilters(DatasetFiltersBase):
    """
    Additional query filters for datasets.
    """
    createdBy: Optional[str] = Field(
        default=None,
        title="Created By",
        description="Filter datasets by the creator's username."
    )

    def filter_createdBy(self, value: str) -> Q:
        """
        Apply a filter for the creator's username.
        """
        return Q(created_by=self.createdBy) if value is not None else Q()



def _create_partial_schema(schema: Type[Schema]) -> Type[Schema]:
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

        if is_optional(annotation):
            annotation = get_args(annotation)
            if len(annotation) > 1:
                annotation = Union[annotation]
            else:
                annotation = get_args(annotation)[0]

        if is_list(annotation):
            list_annotation = get_args(annotation)[0]
            if issubclass(list_annotation, PydanticBaseModel) and not issubclass(list_annotation, CodedConceptSchema):
                related_schema_partial = _create_partial_schema(list_annotation)
                annotation = List[related_schema_partial]        
                
        if issubclass(annotation, PydanticBaseModel) and not issubclass(annotation, CodedConceptSchema):
                annotation = _create_partial_schema(annotation)
        
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
    schema.__name__: _create_partial_schema(schema) for schema in oncology_schemas.ONCOLOGY_SCHEMAS if issubclass(schema, ModelGetSchema)   
}


class PatientCaseDataset(partial_schemas['PatientCase']):
        
    pseudoidentifier: str = Field(title='Pseudoidentifier')
    neoplasticEntities: Optional[List[partial_schemas['NeoplasticEntity']]] = Field( # type: ignore
        default=None, validation_alias=AliasChoices('neoplasticEntities','neoplastic_entities_resources')
    ) 
    tnmStagings: Optional[List[partial_schemas['TNMStaging']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('tnmStagings','tnm_stagings_resources')
    )
    figoStagings: Optional[List[partial_schemas['TNMStaging']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('figoStagings','figo_stagings_resources')
    )
    tumorMarkers: Optional[List[partial_schemas['TumorMarker']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('tumorMarkers','tumor_markers_resources')
    )  
    riskAssessments: Optional[List[partial_schemas['RiskAssessment']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('riskAssessments','risk_assessments_resources')
    )  
    therapyLines: Optional[List[partial_schemas['TherapyLine']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('therapyLines','therapy_lines_resources')
    )  
    systemicTherapies: Optional[List[partial_schemas['SystemicTherapy']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('systemicTherapies','systemic_therapies_resources')
    )  
    surgeries: Optional[List[partial_schemas['Surgery']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('surgeries','surgeries_resources')
    )  
    radiotherapies: Optional[List[partial_schemas['Radiotherapy']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('radiotherapies','radiotherapies_resources'),
    )  
    adverseEvents: Optional[List[partial_schemas['AdverseEvent']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('adverseEvents','adverse_events_resources')
    )  
    treatmentResponses: Optional[List[partial_schemas['TreatmentResponse']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('treatmentResponses','treatment_responses_resources')
    )  
    performanceStatus: Optional[List[partial_schemas['PerformanceStatus']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('performanceStatus','performance_status_resources')
    )  
    comorbidities: Optional[List[partial_schemas['ComorbiditiesAssessment']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('comorbidities','comorbidities_resources')
    )  
    genomicVariants: Optional[List[partial_schemas['GenomicVariant']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('genomicVariants','genomic_variants_resources')
    )  
    genomicSignatures: Optional[List[Union[
        partial_schemas['TumorMutationalBurden'], partial_schemas['MicrosatelliteInstability'], # type: ignore
        partial_schemas['LossOfHeterozygosity'], partial_schemas['HomologousRecombinationDeficiency'], # type: ignore
        partial_schemas['TumorNeoantigenBurden'], partial_schemas['AneuploidScore']]]] = Field( # type: ignore
        default=None, 
    )  
    vitals: Optional[List[partial_schemas['Vitals']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('vitals','vitals_resources')
    )    
    lifestyles: Optional[List[partial_schemas['Lifestyle']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('lifestyles','lifestyles_resources')
    )  
    familyHistory: Optional[List[partial_schemas['FamilyHistory']]] =  Field( # type: ignore
         default=None, validation_alias=AliasChoices('familyHistory','family_histories_resources')
    )  
    vitals: Optional[List[partial_schemas['Vitals']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('vitals','vitals_resources')
    )  
    unspecifiedTumorBoards: Optional[List[partial_schemas['UnspecifiedTumorBoard']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('unspecifiedtumorboards','unspecified_tumor_boards_resources')
    )  
    molecularTumorBoards: Optional[List[partial_schemas['UnspecifiedTumorBoard']]] = Field( # type: ignore
         default=None, validation_alias=AliasChoices('molecularTumorBoards','molecular_tumor_boards_resources')
    )  
    