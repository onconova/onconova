from datetime import datetime
from typing import Dict, List, Union

import pghistory
from django.db.models import Model as DjangoModel
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

import onconova.oncology.schemas as sc
from onconova.core.auth.models import User
from onconova.core.auth.schemas import UserExportSchema
from onconova.core.history.schemas import HistoryEvent
from onconova.oncology.models.patient_case import PatientCaseDataCategories


class ExportMetadata(BaseModel):
    exportedAt: datetime = Field(
        ...,
        title="Export Timestamp",
        description="The datetime when the resource was exported.",
    )
    exportedBy: str = Field(
        ...,
        title="Exported By",
        description="Username of the user who performed the export.",
    )
    exportVersion: str = Field(
        ..., title="Export Version", description="Version tag of the exporting system."
    )
    checksum: str = Field(
        ...,
        title="Export Checksum",
        description="Checksum (e.g., SHA256) of the exported content for integrity verification.",
    )


class PatientCaseBundle(sc.PatientCaseSchema):
    """The order of the properties matters for the import tool (based on references tree)"""

    neoplasticEntities: List[sc.NeoplasticEntitySchema] = Field(
        default=[],
        alias="neoplastic_entities",
        validation_alias=AliasChoices("neoplasticEntities", "neoplastic_entities"),
    )
    stagings: List[
        Union[
            sc.TNMStagingSchema,
            sc.FIGOStagingSchema,
            sc.BinetStagingSchema,
            sc.RaiStagingSchema,
            sc.BreslowDepthSchema,
            sc.ClarkStagingSchema,
            sc.ISSStagingSchema,
            sc.RISSStagingSchema,
            sc.GleasonGradeSchema,
            sc.INSSStageSchema,
            sc.INRGSSStageSchema,
            sc.WilmsStageSchema,
            sc.RhabdomyosarcomaClinicalGroupSchema,
            sc.LymphomaStagingSchema,
        ]
    ] = Field(
        default=[],
    )
    tumorMarkers: List[sc.TumorMarkerSchema] = Field(
        default=[],
        alias="tumor_markers",
        validation_alias=AliasChoices("tumorMarkers", "tumor_markers"),
    )
    riskAssessments: List[sc.RiskAssessmentSchema] = Field(
        default=[],
        alias="risk_assessments",
        validation_alias=AliasChoices("riskAssessments", "risk_assessments"),
    )
    therapyLines: List[sc.TherapyLineSchema] = Field(
        default=[],
        alias="therapy_lines",
        validation_alias=AliasChoices("therapyLines", "therapy_lines"),
    )
    systemicTherapies: List[sc.SystemicTherapySchema] = Field(
        default=[],
        alias="systemic_therapies",
        validation_alias=AliasChoices("systemicTherapies", "systemic_therapies"),
    )
    surgeries: List[sc.SurgerySchema] = Field(
        default=[],
    )
    radiotherapies: List[sc.RadiotherapySchema] = Field(
        default=[],
    )
    adverseEvents: List[sc.AdverseEventSchema] = Field(
        default=[],
        alias="adverse_events",
        validation_alias=AliasChoices("adverseEvents", "adverse_events"),
    )
    treatmentResponses: List[sc.TreatmentResponseSchema] = Field(
        default=[],
        alias="treatment_responses",
        validation_alias=AliasChoices("treatmentResponses", "treatment_responses"),
    )
    performanceStatus: List[sc.PerformanceStatusSchema] = Field(
        default=[],
        alias="performance_status",
        validation_alias=AliasChoices("performanceStatus", "performance_status"),
    )
    comorbidities: List[sc.ComorbiditiesAssessmentSchema] = Field(
        default=[],
    )
    genomicVariants: List[sc.GenomicVariantSchema] = Field(
        default=[],
        alias="genomic_variants",
        validation_alias=AliasChoices("genomicVariants", "genomic_variants"),
    )
    genomicSignatures: List[
        Union[
            sc.TumorMutationalBurdenSchema,
            sc.MicrosatelliteInstabilitySchema,
            sc.LossOfHeterozygositySchema,
            sc.HomologousRecombinationDeficiencySchema,
            sc.TumorNeoantigenBurdenSchema,
            sc.AneuploidScoreSchema,
        ]
    ] = Field(
        default=[],
    )
    vitals: List[sc.VitalsSchema] = Field(
        default=[],
    )
    lifestyles: List[sc.LifestyleSchema] = Field(
        default=[],
    )
    familyHistory: List[sc.FamilyHistorySchema] = Field(
        default=[],
        alias="family_histories",
        validation_alias=AliasChoices("familyHistory", "family_histories"),
    )
    vitals: List[sc.VitalsSchema] = Field(
        default=[],
    )
    tumorBoards: List[
        Union[sc.UnspecifiedTumorBoardSchema, sc.MolecularTumorBoardSchema]
    ] = Field(
        default=[],
    )
    completedDataCategories: Dict[
        PatientCaseDataCategories, sc.PatientCaseDataCompletionStatusSchema
    ]
    history: List[HistoryEvent] = Field(
        default=[],
    )
    contributorsDetails: List[UserExportSchema] = Field(
        default=[]
    )

    model_config = ConfigDict(serialize_by_alias=False)

    @staticmethod
    def resolve_stagings(obj):
        from onconova.oncology.controllers.staging import (
            RESPONSE_SCHEMAS,
            cast_to_model_schema,
        )

        return [
            cast_to_model_schema(staging.get_domain_staging(), RESPONSE_SCHEMAS)
            for staging in obj.stagings.all()
        ]

    @staticmethod
    def resolve_genomicSignatures(obj):
        from onconova.oncology.controllers.genomic_signature import (
            RESPONSE_SCHEMAS,
            cast_to_model_schema,
        )

        return [
            cast_to_model_schema(
                staging.get_discriminated_genomic_signature(), RESPONSE_SCHEMAS
            )
            for staging in obj.genomic_signatures.all()
        ]

    @staticmethod
    def resolve_tumorBoards(obj):
        from onconova.oncology.controllers.tumor_board import (
            RESPONSE_SCHEMAS,
            cast_to_model_schema,
        )

        return [
            cast_to_model_schema(staging.specialized_tumor_board, RESPONSE_SCHEMAS)
            for staging in obj.tumor_boards.all()
        ]

    @staticmethod
    def resolve_completedDataCategories(obj):
        from onconova.oncology.models.patient_case import PatientCase

        return {
            category: sc.PatientCaseDataCompletionStatusSchema(
                status=completion is not None,
                username=completion.created_by if completion else None,
                timestamp=completion.created_at if completion else None,
            )
            for category in PatientCaseDataCategories.values
            for completion in (
                (
                    list(obj.completed_data_categories.filter(category=category))
                    if isinstance(obj, PatientCase)
                    else obj.get("completed_data_categories")
                )
                or [None]
            )
        }

    @staticmethod
    def resolve_history(obj):
        if isinstance(obj, dict):
            return obj.get("history")
        else:
            return (
                pghistory.models.Events.objects.tracks(obj)
                .all()
                .union(
                    pghistory.models.Events.objects.references(obj).filter(
                        pgh_model__icontains="oncology"
                    )
                )
            )
    
    @staticmethod
    def resolve_contributorsDetails(obj):
        if isinstance(obj, dict):
            return obj.get("contributorsDetails")
        else:
            return [
                UserExportSchema(
                    username=user.username, 
                    firstName=user.first_name, 
                    lastName=user.last_name, 
                    anonymized=not user.shareable, 
                    organization=user.organization, 
                    email=user.email, 
                    id=user.id, 
                    externalSource=user.external_source, 
                    externalSourceId=user.external_source_id
                )
                for contributor_username in obj.contributors 
                for user in User.objects.filter(username=contributor_username)
            ]   

    @model_validator(mode='after')
    @classmethod
    def anonymize_users(cls, obj):
        def recursively_replace(obj, original_value, new_value, visited=None):
            if visited is None:
                visited = set()
            # Don't recurse into primitive types
            if isinstance(obj, (str, int, float, bool, type(None))):
                return
            # Avoid cycles
            obj_id = id(obj)
            if obj_id in visited:
                return
            visited.add(obj_id)

            if isinstance(obj, dict):
                for key, value in obj.items():
                    if value == original_value:
                        obj[key] = new_value
                    else:
                        recursively_replace(value, original_value, new_value, visited)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    if item == original_value:
                        obj[idx] = new_value
                    else:
                        recursively_replace(item, original_value, new_value, visited)
            elif hasattr(obj, '__dict__'):
                for attr in vars(obj):
                    value = getattr(obj, attr)
                    if value == original_value:
                        setattr(obj, attr, new_value)
                    else:
                        recursively_replace(value, original_value, new_value, visited)
                        
        for user in obj.contributorsDetails:
            if not user.anonymized:
                continue
            original_username = user.username
            # Anonymize user details
            user.firstName = 'Anonymous'
            user.lastName = 'External User'
            user.username = f"user-{str(user.id)[:5]}" # type: ignore
            user.email = 'anonymized@mail.com'
            # Replace all existing instances of the username throughout the bundle and replace it
            recursively_replace(obj, original_username, user.username)
            
        return obj 