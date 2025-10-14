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
    RadiotherapyCreateSchema,
    RadiotherapyDosageCreateSchema,
    RadiotherapyDosageSchema,
    RadiotherapySchema,
    RadiotherapySettingCreateSchema,
    RadiotherapySettingSchema,
)
from .risk_assessment import RiskAssessmentCreateSchema, RiskAssessmentSchema
from .staging import (
    BinetStagingCreateSchema,
    BinetStagingSchema,
    BreslowDepthCreateSchema,
    BreslowDepthSchema,
    ClarkStagingCreateSchema,
    ClarkStagingSchema,
    FIGOStagingCreateSchema,
    FIGOStagingSchema,
    GleasonGradeCreateSchema,
    GleasonGradeSchema,
    INRGSSStageCreateSchema,
    INRGSSStageSchema,
    INSSStageCreateSchema,
    INSSStageSchema,
    ISSStagingCreateSchema,
    ISSStagingSchema,
    LymphomaStagingCreateSchema,
    LymphomaStagingSchema,
    RaiStagingCreateSchema,
    RaiStagingSchema,
    RhabdomyosarcomaClinicalGroupCreateSchema,
    RhabdomyosarcomaClinicalGroupSchema,
    RISSStagingCreateSchema,
    RISSStagingSchema,
    StagingSchema,
    TNMStagingCreateSchema,
    TNMStagingSchema,
    WilmsStageCreateSchema,
    WilmsStageSchema,
)
from .surgery import SurgeryCreateSchema, SurgerySchema
from .systemic_therapy import (
    SystemicTherapyCreateSchema,
    SystemicTherapyMedicationCreateSchema,
    SystemicTherapyMedicationSchema,
    SystemicTherapySchema,
)
from .therapy_line import TherapyLineCreateSchema, TherapyLineSchema
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
StagingFilters = create_filters_schema(schema=StagingSchema, name="StagingFilters")
RiskAssessmentFilters = create_filters_schema(
    schema=RiskAssessmentSchema, name="RiskAssessmentFilters"
)
SystemicTherapyFilters = create_filters_schema(
    schema=SystemicTherapySchema, name="SystemicTherapyFilters"
)
SurgeryFilters = create_filters_schema(schema=SurgerySchema, name="SurgeryFilters")
RadiotherapyFilters = create_filters_schema(
    schema=RadiotherapySchema, name="RadiotherapyFilters"
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
    schema=TherapyLineSchema, name="TherapyLineFilters"
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
    TNMStagingSchema,
    TNMStagingCreateSchema,
    FIGOStagingSchema,
    FIGOStagingCreateSchema,
    BinetStagingSchema,
    BinetStagingCreateSchema,
    RaiStagingSchema,
    RaiStagingCreateSchema,
    BreslowDepthSchema,
    BreslowDepthCreateSchema,
    ClarkStagingSchema,
    ClarkStagingCreateSchema,
    ISSStagingSchema,
    ISSStagingCreateSchema,
    RISSStagingSchema,
    RISSStagingCreateSchema,
    GleasonGradeSchema,
    GleasonGradeCreateSchema,
    INSSStageSchema,
    INSSStageCreateSchema,
    INRGSSStageSchema,
    INRGSSStageCreateSchema,
    WilmsStageSchema,
    WilmsStageCreateSchema,
    RhabdomyosarcomaClinicalGroupSchema,
    RhabdomyosarcomaClinicalGroupCreateSchema,
    LymphomaStagingSchema,
    LymphomaStagingCreateSchema,
    # Tumor marker schemas
    TumorMarkerSchema,
    TumorMarkerCreateSchema,
    # Risk assessment schemas
    RiskAssessmentSchema,
    RiskAssessmentCreateSchema,
    # Therapy line schemas
    TherapyLineSchema,
    TherapyLineCreateSchema,
    # Systemic therapy schemas
    SystemicTherapySchema,
    SystemicTherapyCreateSchema,
    SystemicTherapyMedicationSchema,
    SystemicTherapyMedicationCreateSchema,
    # Surgery schemas
    SurgerySchema,
    SurgeryCreateSchema,
    # Radiotherapy schemas
    RadiotherapySchema,
    RadiotherapyCreateSchema,
    RadiotherapyDosageSchema,
    RadiotherapyDosageCreateSchema,
    RadiotherapySettingSchema,
    RadiotherapySettingCreateSchema,
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
