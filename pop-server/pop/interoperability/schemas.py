from datetime import datetime
from typing import List, Union, Dict
from pydantic import Field, AliasChoices, BaseModel 
from pop.oncology.models.patient_case import PatientCaseDataCategories
import pop.oncology.schemas as sc

class ExportMetadata(BaseModel):
    exported_at: datetime = Field(
        ...,
        title="Export Timestamp",
        description="The datetime when the resource was exported."
    )
    exported_by: str = Field(
        ...,
        title="Exported By",
        description="Username of the user who performed the export."
    )
    export_version: str = Field(
        ...,
        title="Export Version",
        description="Version tag of the exporting system."
    )
    checksum: str = Field(
        ...,
        title="Export Checksum",
        description="Checksum (e.g., SHA256) of the exported content for integrity verification."
    )
    
class PatientCaseBundle(sc.PatientCaseSchema):
    """ The order of the properties matters for the import tool (based on references tree)"""
    neoplasticEntities: List[sc.NeoplasticEntitySchema] = Field(
        default=[], 
        alias='neoplastic_entities', 
        validation_alias=AliasChoices('neoplastic_entities','neoplasticEntities')
    ) 
    stagings: List[Union[sc.TNMStagingSchema, sc.FIGOStagingSchema, sc.BinetStagingSchema, 
                        sc.RaiStagingSchema, sc.BreslowDepthSchema, sc.ClarkStagingSchema, 
                        sc.ISSStagingSchema, sc.RISSStagingSchema,  sc.GleasonGradeSchema, 
                        sc.INSSStageSchema, sc.INRGSSStageSchema, sc.WilmsStageSchema, 
                        sc.RhabdomyosarcomaClinicalGroupSchema, sc.LymphomaStagingSchema]] = Field(
        default=[], 
    ) 
    tumorMarkers: List[sc.TumorMarkerSchema] = Field(
        default=[], 
        alias='tumor_markers', 
        validation_alias=AliasChoices('tumor_markers','tumorMarkers')
    )  
    riskAssessments: List[sc.RiskAssessmentSchema] = Field(
        default=[], 
        alias='risk_assessments', 
        validation_alias=AliasChoices('risk_assessments','riskAssessments')
    )  
    therapyLines: List[sc.TherapyLineSchema] = Field(
        default=[], 
        alias='therapy_lines', 
        validation_alias=AliasChoices('therapy_lines','therapyLines')
    )  
    systemicTherapies: List[sc.SystemicTherapySchema] = Field(
        default=[], 
        alias='systemic_therapies', 
        validation_alias=AliasChoices('systemic_therapies','systemicTherapies')
    )  
    surgeries: List[sc.SurgerySchema] = Field(
        default=[], 
    )  
    radiotherapies: List[sc.RadiotherapySchema] = Field(
        default=[], 
    )  
    adverseEvents: List[sc.AdverseEventSchema] = Field(
        default=[], 
        alias='adverse_events', 
        validation_alias=AliasChoices('adverse_events','adverseEvents')
    )  
    treatmentResponses: List[sc.TreatmentResponseSchema] = Field(
        default=[], 
        alias='treatment_responses', 
        validation_alias=AliasChoices('treatment_responses','treatmentResponses')
    )  
    performanceStatus: List[sc.PerformanceStatusSchema] = Field(
        default=[], 
        alias='performance_status', 
        validation_alias=AliasChoices('performance_status','performanceStatus')
    )  
    comorbidities: List[sc.ComorbiditiesAssessmentSchema] = Field(
        default=[], 
    )  
    genomicVariants: List[sc.GenomicVariantSchema] = Field(
        default=[], 
        alias='genomic_variants', 
        validation_alias=AliasChoices('genomic_variants','genomicVariants')
    )  
    genomicSignatures: List[Union[
        sc.TumorMutationalBurdenSchema, sc.MicrosatelliteInstabilitySchema,
        sc.LossOfHeterozygositySchema, sc.HomologousRecombinationDeficiencySchema,
        sc.TumorNeoantigenBurdenSchema, sc.AneuploidScoreSchema]] = Field(
        default=[], 
    )  
    vitals: List[sc.VitalsSchema] = Field(
        default=[], 
    )    
    lifestyles: List[sc.LifestyleSchema] = Field(
        default=[], 
    )  
    familyHistory: List[sc.FamilyHistorySchema] =  Field(
        default=[], 
        alias='family_histories', 
        validation_alias=AliasChoices('family_histories','familyHistory')
    )  
    vitals: List[sc.VitalsSchema] = Field(
        default=[], 
    )  
    tumorBoards: List[Union[sc.UnspecifiedTumorBoardSchema, sc.MolecularTumorBoardSchema]] = Field(
        default=[], 
    )  
    completedDataCategories: Dict[PatientCaseDataCategories, sc.PatientCaseDataCompletionStatusSchema]
    
    @staticmethod
    def resolve_stagings(obj):
        from pop.oncology.controllers.staging import cast_to_model_schema, RESPONSE_SCHEMAS
        return [cast_to_model_schema(staging.get_domain_staging(), RESPONSE_SCHEMAS) for staging in obj.stagings.all()]

    @staticmethod
    def resolve_genomicSignatures(obj):
        from pop.oncology.controllers.genomic_signature import cast_to_model_schema, RESPONSE_SCHEMAS
        return [cast_to_model_schema(staging.get_discriminated_genomic_signature(), RESPONSE_SCHEMAS) for staging in obj.genomic_signatures.all()]

    @staticmethod
    def resolve_tumorBoards(obj):
        from pop.oncology.controllers.tumor_board import cast_to_model_schema, RESPONSE_SCHEMAS
        return [cast_to_model_schema(staging.specialized_tumor_board, RESPONSE_SCHEMAS) for staging in obj.tumor_boards.all()]

    @staticmethod
    def resolve_completedDataCategories(obj):
        from pop.oncology.models.patient_case import PatientCase
        return {category: sc.PatientCaseDataCompletionStatusSchema(
                status=completion is not None,
                username= completion.created_by if completion else None,
                timestamp=completion.created_at if completion else None,
        ) for category in PatientCaseDataCategories.values for completion in (
            (
                list(obj.completed_data_categories.filter(category=category)) 
                    if isinstance(obj, PatientCase) 
                    else obj.get('completed_data_categories')
            ) or [None]
        )}
