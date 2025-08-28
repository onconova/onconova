from onconova.core.serialization.factory import create_filters_schema

from .adverse_event import (
    AdverseEventCreateSchema,
    AdverseEventMitigationCreateSchema,
    AdverseEventMitigationSchema,
    AdverseEventSchema,
    AdverseEventSuspectedCauseCreateSchema,
    AdverseEventSuspectedCauseSchema,
)
from .comorbidities import (
    ComorbiditiesAssessmentCreateSchema,
    ComorbiditiesAssessmentSchema,
    ComorbiditiesPanel,
    ComorbidityPanelCategory,
)
from .family_history import FamilyHistoryCreateSchema, FamilyHistorySchema
from .genomic_signature import (
    AneuploidScoreCreateSchema,
    AneuploidScoreSchema,
    GenomicSignatureSchema,
    HomologousRecombinationDeficiencyCreateSchema,
    HomologousRecombinationDeficiencySchema,
    LossOfHeterozygosityCreateSchema,
    LossOfHeterozygositySchema,
    MicrosatelliteInstabilityCreateSchema,
    MicrosatelliteInstabilitySchema,
    TumorMutationalBurdenCreateSchema,
    TumorMutationalBurdenSchema,
    TumorNeoantigenBurdenCreateSchema,
    TumorNeoantigenBurdenSchema,
)
from .genomic_variant import GenomicVariantCreateSchema, GenomicVariantSchema
from .lifestyle import LifestyleCreateSchema, LifestyleSchema
from .neoplastic_entity import NeoplasticEntityCreateSchema, NeoplasticEntitySchema
from .patient_case import (
    PatientCaseCreateSchema,
    PatientCaseDataCompletionStatusSchema,
    PatientCaseSchema,
)
from .performance_status import PerformanceStatusCreateSchema, PerformanceStatusSchema
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
    schema=PatientCaseSchema,
    name="PatientCaseFilters",
    exclude=["clinicalIdentifier", "dateOfBirth", "dateOfDeath", "clinicalCenter"],
)
NeoplasticEntityFilters = create_filters_schema(
    schema=NeoplasticEntitySchema, name="NeoplasticEntityFilters"
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
    schema=AdverseEventSchema, name="AdverseEventFilters"
)
TreatmentResponseFilters = create_filters_schema(
    schema=TreatmentResponseSchema, name="TreatmentResponseFilters"
)
PerformanceStatusFilters = create_filters_schema(
    schema=PerformanceStatusSchema, name="PerformanceStatusFilters"
)
LifestyleFilters = create_filters_schema(
    schema=LifestyleSchema, name="LifestyleFilters"
)
FamilyHistoryFilters = create_filters_schema(
    schema=FamilyHistorySchema, name="FamilyHistoryFilters"
)
TumorBoardFilters = create_filters_schema(
    schema=UnspecifiedTumorBoardSchema, name="TumorBoardFilters"
)
VitalsFilters = create_filters_schema(schema=VitalsSchema, name="VitalsFilters")
ComorbiditiesAssessmentFilters = create_filters_schema(
    schema=ComorbiditiesAssessmentSchema, name="ComorbiditiesAssessmentFilters"
)
GenomicVariantFilters = create_filters_schema(
    schema=GenomicVariantSchema, name="GenomicVariantFilters"
)
GenomicSignatureFilters = create_filters_schema(
    schema=GenomicSignatureSchema, name="GenomicSignatureFilters"
)
TherapyLineFilters = create_filters_schema(
    schema=TherapyLineSchema, name="TherapyLineFilters"
)

ONCOLOGY_SCHEMAS = (
    # PatientCase schemas
    PatientCaseSchema,
    PatientCaseCreateSchema,
    PatientCaseDataCompletionStatusSchema,
    # Neoplastic entity schemas
    NeoplasticEntitySchema,
    NeoplasticEntityCreateSchema,
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
    AdverseEventSchema,
    AdverseEventCreateSchema,
    AdverseEventSuspectedCauseSchema,
    AdverseEventSuspectedCauseCreateSchema,
    AdverseEventMitigationSchema,
    AdverseEventMitigationCreateSchema,
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
    PerformanceStatusSchema,
    PerformanceStatusCreateSchema,
    # Lifestyle schemas
    LifestyleSchema,
    LifestyleCreateSchema,
    # Family member history schemas
    FamilyHistorySchema,
    FamilyHistoryCreateSchema,
    # Vitals
    VitalsSchema,
    VitalsCreateSchema,
    # Comorbidities
    ComorbiditiesAssessmentSchema,
    ComorbiditiesAssessmentCreateSchema,
    ComorbiditiesPanel,
    ComorbidityPanelCategory,
    # Genomic variant schemas
    GenomicVariantSchema,
    GenomicVariantCreateSchema,
    # Genomic signature schemas
    GenomicSignatureSchema,
    TumorMutationalBurdenSchema,
    TumorMutationalBurdenCreateSchema,
    MicrosatelliteInstabilitySchema,
    MicrosatelliteInstabilityCreateSchema,
    LossOfHeterozygositySchema,
    LossOfHeterozygosityCreateSchema,
    HomologousRecombinationDeficiencySchema,
    HomologousRecombinationDeficiencyCreateSchema,
    TumorNeoantigenBurdenSchema,
    TumorNeoantigenBurdenCreateSchema,
    AneuploidScoreSchema,
    AneuploidScoreCreateSchema,
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

__all__ = [schema.__name__ for schema in ONCOLOGY_SCHEMAS]
