from onconova.core.serialization.factory import create_filters_schema

from .adverse_event import (
    AdverseEventCreate,
    AdverseEventMitigationCreate,
    AdverseEventMitigation,
    AdverseEvent,
    AdverseEventSuspectedCauseCreate,
    AdverseEventSuspectedCause,
)
from .comorbidities import (
    ComorbiditiesAssessmentCreate,
    ComorbiditiesAssessment,
    ComorbiditiesPanel,
    ComorbidityPanelCategory,
)
from .family_history import FamilyHistoryCreate, FamilyHistory
from .genomic_signature import (
    AneuploidScoreCreate,
    AneuploidScore,
    GenomicSignature,
    HomologousRecombinationDeficiencyCreate,
    HomologousRecombinationDeficiency,
    LossOfHeterozygosityCreate,
    LossOfHeterozygosity,
    MicrosatelliteInstabilityCreate,
    MicrosatelliteInstability,
    TumorMutationalBurdenCreate,
    TumorMutationalBurden,
    TumorNeoantigenBurdenCreate,
    TumorNeoantigenBurden,
)
from .genomic_variant import GenomicVariantCreate, GenomicVariant
from .lifestyle import LifestyleCreate, Lifestyle
from .neoplastic_entity import NeoplasticEntityCreate, NeoplasticEntity
from .patient_case import (
    PatientCaseCreate,
    PatientCaseDataCompletionStatus,
    PatientCase,
)
from .performance_status import PerformanceStatusCreate, PerformanceStatus
from .radiotherapy import (
    RadiotherapyCreate,
    RadiotherapyDosageCreate,
    RadiotherapyDosage,
    Radiotherapy,
    RadiotherapySettingCreate,
    RadiotherapySetting,
)
from .risk_assessment import RiskAssessmentCreate, RiskAssessment
from .staging import (
    BinetStagingCreate,
    BinetStaging,
    BreslowDepthCreate,
    BreslowDepth,
    ClarkStagingCreate,
    ClarkStaging,
    FIGOStagingCreate,
    FIGOStaging,
    GleasonGradeCreate,
    GleasonGrade,
    INRGSSStageCreate,
    INRGSSStage,
    INSSStageCreate,
    INSSStage,
    ISSStagingCreate,
    ISSStaging,
    LymphomaStagingCreate,
    LymphomaStaging,
    RaiStagingCreate,
    RaiStaging,
    RhabdomyosarcomaClinicalGroupCreate,
    RhabdomyosarcomaClinicalGroup,
    RISSStagingCreate,
    RISSStaging,
    Staging,
    TNMStagingCreate,
    TNMStaging,
    WilmsStageCreate,
    WilmsStage,
)
from .surgery import SurgeryCreate, Surgery
from .systemic_therapy import (
    SystemicTherapyCreate,
    SystemicTherapyMedicationCreate,
    SystemicTherapyMedication,
    SystemicTherapy,
)
from .therapy_line import TherapyLineCreate, TherapyLine
from .treatment_response import TreatmentResponseCreateSchema, TreatmentResponseSchema
from .tumor_board import (
    MolecularTherapeuticRecommendationCreateSchema,
    MolecularTherapeuticRecommendationSchema,
    MolecularTumorBoardCreateSchema,
    MolecularTumorBoardSchema,
    UnspecifiedTumorBoardCreateSchema,
    UnspecifiedTumorBoardSchema,
)
from .tumor_marker import TumorMarkerCreateSchema, TumorMarkerSchema
from .vitals import VitalsCreateSchema, VitalsSchema

# Filter schemas
PatientCaseFilters = create_filters_schema(
    schema=PatientCase,
    name="PatientCaseFilters",
    exclude=["clinicalIdentifier", "dateOfBirth", "dateOfDeath", "clinicalCenter"],
)
NeoplasticEntityFilters = create_filters_schema(
    schema=NeoplasticEntity, name="NeoplasticEntityFilters"
)
TumorMarkerFilters = create_filters_schema(
    schema=TumorMarkerSchema, name="TumorMarkerFilters"
)
StagingFilters = create_filters_schema(schema=Staging, name="StagingFilters")
RiskAssessmentFilters = create_filters_schema(
    schema=RiskAssessment, name="RiskAssessmentFilters"
)
SystemicTherapyFilters = create_filters_schema(
    schema=SystemicTherapy, name="SystemicTherapyFilters"
)
SurgeryFilters = create_filters_schema(schema=Surgery, name="SurgeryFilters")
RadiotherapyFilters = create_filters_schema(
    schema=Radiotherapy, name="RadiotherapyFilters"
)
AdverseEventFilters = create_filters_schema(
    schema=AdverseEvent, name="AdverseEventFilters"
)
TreatmentResponseFilters = create_filters_schema(
    schema=TreatmentResponseSchema, name="TreatmentResponseFilters"
)
PerformanceStatusFilters = create_filters_schema(
    schema=PerformanceStatus, name="PerformanceStatusFilters"
)
LifestyleFilters = create_filters_schema(
    schema=Lifestyle, name="LifestyleFilters"
)
FamilyHistoryFilters = create_filters_schema(
    schema=FamilyHistory, name="FamilyHistoryFilters"
)
TumorBoardFilters = create_filters_schema(
    schema=UnspecifiedTumorBoardSchema, name="TumorBoardFilters"
)
VitalsFilters = create_filters_schema(schema=VitalsSchema, name="VitalsFilters")
ComorbiditiesAssessmentFilters = create_filters_schema(
    schema=ComorbiditiesAssessment, name="ComorbiditiesAssessmentFilters"
)
GenomicVariantFilters = create_filters_schema(
    schema=GenomicVariant, name="GenomicVariantFilters"
)
GenomicSignatureFilters = create_filters_schema(
    schema=GenomicSignature, name="GenomicSignatureFilters"
)
TherapyLineFilters = create_filters_schema(
    schema=TherapyLine, name="TherapyLineFilters"
)

ONCOLOGY_SCHEMAS = (
    # PatientCase schemas
    PatientCase,
    PatientCaseCreate,
    PatientCaseDataCompletionStatus,
    # Neoplastic entity schemas
    NeoplasticEntity,
    NeoplasticEntityCreate,
    # Staging schemas
    TNMStaging,
    TNMStagingCreate,
    FIGOStaging,
    FIGOStagingCreate,
    BinetStaging,
    BinetStagingCreate,
    RaiStaging,
    RaiStagingCreate,
    BreslowDepth,
    BreslowDepthCreate,
    ClarkStaging,
    ClarkStagingCreate,
    ISSStaging,
    ISSStagingCreate,
    RISSStaging,
    RISSStagingCreate,
    GleasonGrade,
    GleasonGradeCreate,
    INSSStage,
    INSSStageCreate,
    INRGSSStage,
    INRGSSStageCreate,
    WilmsStage,
    WilmsStageCreate,
    RhabdomyosarcomaClinicalGroup,
    RhabdomyosarcomaClinicalGroupCreate,
    LymphomaStaging,
    LymphomaStagingCreate,
    # Tumor marker schemas
    TumorMarkerSchema,
    TumorMarkerCreateSchema,
    # Risk assessment schemas
    RiskAssessment,
    RiskAssessmentCreate,
    # Therapy line schemas
    TherapyLine,
    TherapyLineCreate,
    # Systemic therapy schemas
    SystemicTherapy,
    SystemicTherapyCreate,
    SystemicTherapyMedication,
    SystemicTherapyMedicationCreate,
    # Surgery schemas
    Surgery,
    SurgeryCreate,
    # Radiotherapy schemas
    Radiotherapy,
    RadiotherapyCreate,
    RadiotherapyDosage,
    RadiotherapyDosageCreate,
    RadiotherapySetting,
    RadiotherapySettingCreate,
    # Adverse event schemas
    AdverseEvent,
    AdverseEventCreate,
    AdverseEventSuspectedCause,
    AdverseEventSuspectedCauseCreate,
    AdverseEventMitigation,
    AdverseEventMitigationCreate,
    # Treatment response schemas
    TreatmentResponseSchema,
    TreatmentResponseCreateSchema,
    # Tumor board schemas
    UnspecifiedTumorBoardSchema,
    UnspecifiedTumorBoardCreateSchema,
    MolecularTumorBoardSchema,
    MolecularTumorBoardCreateSchema,
    MolecularTherapeuticRecommendationSchema,
    MolecularTherapeuticRecommendationCreateSchema,
    # Performance status schemas
    PerformanceStatus,
    PerformanceStatusCreate,
    # Lifestyle schemas
    Lifestyle,
    LifestyleCreate,
    # Family member history schemas
    FamilyHistory,
    FamilyHistoryCreate,
    # Vitals
    VitalsSchema,
    VitalsCreateSchema,
    # Comorbidities
    ComorbiditiesAssessment,
    ComorbiditiesAssessmentCreate,
    ComorbiditiesPanel,
    ComorbidityPanelCategory,
    # Genomic variant schemas
    GenomicVariant,
    GenomicVariantCreate,
    # Genomic signature schemas
    GenomicSignature,
    TumorMutationalBurden,
    TumorMutationalBurdenCreate,
    MicrosatelliteInstability,
    MicrosatelliteInstabilityCreate,
    LossOfHeterozygosity,
    LossOfHeterozygosityCreate,
    HomologousRecombinationDeficiency,
    HomologousRecombinationDeficiencyCreate,
    TumorNeoantigenBurden,
    TumorNeoantigenBurdenCreate,
    AneuploidScore,
    AneuploidScoreCreate,
    # Filters
    PatientCaseFilters,
    NeoplasticEntityFilters,
    TumorMarkerFilters,
    RiskAssessmentFilters,
    StagingFilters,
    SystemicTherapyFilters,
    SurgeryFilters,
    RadiotherapyFilters,
    AdverseEventFilters,
    TreatmentResponseFilters,
    TumorBoardFilters,
    PerformanceStatusFilters,
    LifestyleFilters,
    VitalsFilters,
    ComorbiditiesAssessmentFilters,
    GenomicVariantFilters,
    GenomicSignatureFilters,
    TumorBoardFilters,
)

__all__ = [schema.__name__ for schema in ONCOLOGY_SCHEMAS] # type: ignore
