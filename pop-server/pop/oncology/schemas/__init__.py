from pop.core.schemas.factory import create_filters_schema
from .patient_case import (
    PatientCaseFilters,
    PatientCaseSchema, PatientCaseCreateSchema,
    PatientCaseDataCompletionStatusSchema, 
    PatientCaseBundleSchema, PatientCaseBundleCreateSchema
)
from .neoplastic_entity import NeoplasticEntitySchema, NeoplasticEntityCreateSchema
from .staging import (
    StagingSchema,
    TNMStagingSchema, TNMStagingCreateSchema,
    FIGOStagingSchema, FIGOStagingCreateSchema,
    BinetStagingSchema, BinetStagingCreateSchema,
    RaiStagingSchema, RaiStagingCreateSchema,
    BreslowDepthSchema, BreslowDepthCreateSchema,
    ClarkStagingSchema, ClarkStagingCreateSchema,
    ISSStagingSchema, ISSStagingCreateSchema,
    RISSStagingSchema, RISSStagingCreateSchema, 
    GleasonGradeSchema, GleasonGradeCreateSchema,
    INSSStageSchema, INSSStageCreateSchema, 
    INRGSSStageSchema, INRGSSStageCreateSchema,
    WilmsStageSchema, WilmsStageCreateSchema,
    RhabdomyosarcomaClinicalGroupSchema, RhabdomyosarcomaClinicalGroupCreateSchema,
    LymphomaStagingSchema, LymphomaStagingCreateSchema,
)
from .therapy_line import TherapyLineSchema, TherapyLineCreateSchema
from .tumor_marker import TumorMarkerSchema, TumorMarkerCreateSchema
from .risk_assessment import RiskAssessmentSchema, RiskAssessmentCreateSchema
from .systemic_therapy import (
    SystemicTherapySchema, SystemicTherapyCreateSchema, 
    SystemicTherapyMedicationSchema, SystemicTherapyMedicationCreateSchema,
)
from .surgery import SurgerySchema, SurgeryCreateSchema 
from .radiotherapy import (
    RadiotherapySchema, RadiotherapyCreateSchema, 
    RadiotherapyDosageSchema, RadiotherapyDosageCreateSchema,
    RadiotherapySettingSchema, RadiotherapySettingCreateSchema,
)
from .performance_status import PerformanceStatusSchema, PerformanceStatusCreateSchema
from .adverse_event import (
    AdverseEventSchema, AdverseEventCreateSchema,
    AdverseEventSuspectedCauseSchema, AdverseEventSuspectedCauseCreateSchema,
    AdverseEventMitigationSchema, AdverseEventMitigationCreateSchema
)
from .lifestyle import LifestyleSchema, LifestyleCreateSchema
from .family_history import FamilyHistorySchema, FamilyHistoryCreateSchema
from .vitals import VitalsSchema, VitalsCreateSchema
from .treatment_response import TreatmentResponseSchema, TreatmentResponseCreateSchema
from .tumor_board import (
    TumorBoardSchema,
    UnspecifiedTumorBoardSchema, UnspecifiedTumorBoardCreateSchema,
    MolecularTumorBoardSchema, MolecularTumorBoardCreateSchema,
    MolecularTherapeuticRecommendationSchema, MolecularTherapeuticRecommendationCreateSchema
)
from .comorbidities import ComorbiditiesAssessmentSchema, ComorbiditiesAssessmentCreateSchema, ComorbiditiesPanel, ComorbidityPanelCategory
from .genomic_variant import GenomicVariantSchema, GenomicVariantCreateSchema
from .genomic_signature import (
    GenomicSignatureSchema,
    TumorMutationalBurdenSchema, TumorMutationalBurdenCreateSchema,
    MicrosatelliteInstabilitySchema, MicrosatelliteInstabilityCreateSchema,
    LossOfHeterozygositySchema, LossOfHeterozygosityCreateSchema,
    HomologousRecombinationDeficiencySchema, HomologousRecombinationDeficiencyCreateSchema,
    TumorNeoantigenBurdenSchema, TumorNeoantigenBurdenCreateSchema,
    AneuploidScoreSchema, AneuploidScoreCreateSchema,
)

# Filter schemas
NeoplasticEntityFilters = create_filters_schema(schema = NeoplasticEntitySchema, name='NeoplasticEntityFilters')
TumorMarkerFilters = create_filters_schema(schema = TumorMarkerSchema, name='TumorMarkerFilters')
StagingFilters = create_filters_schema(schema = StagingSchema, name='StagingFilters')
RiskAssessmentFilters = create_filters_schema(schema = RiskAssessmentSchema, name='RiskAssessmentFilters')
SystemicTherapyFilters = create_filters_schema(schema = SystemicTherapySchema, name='SystemicTherapyFilters')
SurgeryFilters = create_filters_schema(schema = SurgerySchema, name='SurgeryFilters')
RadiotherapyFilters = create_filters_schema(schema = RadiotherapySchema, name='RadiotherapyFilters')
AdverseEventFilters = create_filters_schema(schema = AdverseEventSchema, name='AdverseEventFilters')
TreatmentResponseFilters = create_filters_schema(schema = TreatmentResponseSchema, name='TreatmentResponseFilters')
TumorBoardFilters = create_filters_schema(schema = TumorBoardSchema, name='TumorBoardFilters')
PerformanceStatusFilters = create_filters_schema(schema = PerformanceStatusSchema, name='PerformanceStatusFilters')
LifestyleFilters = create_filters_schema(schema = LifestyleSchema, name='LifestyleFilters')
FamilyHistoryFilters = create_filters_schema(schema = FamilyHistorySchema, name='FamilyHistoryFilters')
TumorBoardFilters = create_filters_schema(schema = UnspecifiedTumorBoardSchema, name='TumorBoardFilters')
VitalsFilters = create_filters_schema(schema = VitalsSchema, name='VitalsFilters')
ComorbiditiesAssessmentFilters = create_filters_schema(schema = ComorbiditiesAssessmentSchema, name='ComorbiditiesAssessmentFilters')
GenomicVariantFilters = create_filters_schema(schema = GenomicVariantSchema, name='GenomicVariantFilters')
GenomicSignatureFilters = create_filters_schema(schema=GenomicSignatureSchema, name='GenomicSignatureFilters')
TherapyLineFilters = create_filters_schema(schema=TherapyLineSchema, name='TherapyLineFilters')

ONCOLOGY_SCHEMAS = (
    # PatientCase schemas
    PatientCaseSchema, PatientCaseCreateSchema,
    PatientCaseDataCompletionStatusSchema, 
    PatientCaseBundleSchema, PatientCaseBundleCreateSchema,
    # Neoplastic entity schemas
    NeoplasticEntitySchema, NeoplasticEntityCreateSchema,
    # Staging schemas
    TNMStagingSchema, TNMStagingCreateSchema,
    FIGOStagingSchema, FIGOStagingCreateSchema,
    BinetStagingSchema, BinetStagingCreateSchema,
    RaiStagingSchema, RaiStagingCreateSchema,
    BreslowDepthSchema, BreslowDepthCreateSchema,
    ClarkStagingSchema, ClarkStagingCreateSchema,
    ISSStagingSchema, ISSStagingCreateSchema,
    RISSStagingSchema, RISSStagingCreateSchema, 
    GleasonGradeSchema, GleasonGradeCreateSchema,
    INSSStageSchema, INSSStageCreateSchema, 
    INRGSSStageSchema, INRGSSStageCreateSchema,
    WilmsStageSchema, WilmsStageCreateSchema,
    RhabdomyosarcomaClinicalGroupSchema, RhabdomyosarcomaClinicalGroupCreateSchema,
    LymphomaStagingSchema, LymphomaStagingCreateSchema,
    # Tumor marker schemas
    TumorMarkerSchema, TumorMarkerCreateSchema,
    # Risk assessment schemas
    RiskAssessmentSchema, RiskAssessmentCreateSchema,
    # Therapy line schemas
    TherapyLineSchema, TherapyLineCreateSchema,
    # Systemic therapy schemas 
    SystemicTherapySchema, SystemicTherapyCreateSchema, 
    SystemicTherapyMedicationSchema, SystemicTherapyMedicationCreateSchema,
    # Surgery schemas
    SurgerySchema, SurgeryCreateSchema,
    # Radiotherapy schemas
    RadiotherapySchema, RadiotherapyCreateSchema, 
    RadiotherapyDosageSchema, RadiotherapyDosageCreateSchema,
    RadiotherapySettingSchema, RadiotherapySettingCreateSchema,
    # Adverse event schemas 
    AdverseEventSchema, AdverseEventCreateSchema,
    AdverseEventSuspectedCauseSchema, AdverseEventSuspectedCauseCreateSchema,
    AdverseEventMitigationSchema, AdverseEventMitigationCreateSchema,    
    # Treatment response schemas 
    TreatmentResponseSchema, TreatmentResponseCreateSchema,
    # Tumor board schemas 
    TumorBoardSchema,
    UnspecifiedTumorBoardSchema, UnspecifiedTumorBoardCreateSchema,
    MolecularTumorBoardSchema, MolecularTumorBoardCreateSchema,
    MolecularTherapeuticRecommendationSchema, MolecularTherapeuticRecommendationCreateSchema,
    # Performance status schemas 
    PerformanceStatusSchema, PerformanceStatusCreateSchema,
    # Lifestyle schemas
    LifestyleSchema, LifestyleCreateSchema,
    # Family member history schemas 
    FamilyHistorySchema, FamilyHistoryCreateSchema, 
    # Vitals 
    VitalsSchema, VitalsCreateSchema,
    # Comorbidities
    ComorbiditiesAssessmentSchema, ComorbiditiesAssessmentCreateSchema, ComorbiditiesPanel, ComorbidityPanelCategory,
    # Genomic variant schemas 
    GenomicVariantSchema, GenomicVariantCreateSchema,
    # Genomic signature schemas
    GenomicSignatureSchema,
    TumorMutationalBurdenSchema, TumorMutationalBurdenCreateSchema,
    MicrosatelliteInstabilitySchema, MicrosatelliteInstabilityCreateSchema,
    LossOfHeterozygositySchema, LossOfHeterozygosityCreateSchema,
    HomologousRecombinationDeficiencySchema, HomologousRecombinationDeficiencyCreateSchema,
    TumorNeoantigenBurdenSchema, TumorNeoantigenBurdenCreateSchema,
    AneuploidScoreSchema, AneuploidScoreCreateSchema,
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