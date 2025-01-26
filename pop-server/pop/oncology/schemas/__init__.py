from pop.core.schemas import create_filters_schema
from .PatientCase import (
    PatientCaseSchema, PatientCaseCreateSchema,
    PatientCaseDataCompletionStatusSchema, 
    PatientCaseBundleSchema, PatientCaseBundleCreateSchema
)
from .NeoplasticEntity import NeoplasticEntitySchema, NeoplasticEntityCreateSchema
from .Staging import (
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
from .TumorMarker import TumorMarkerSchema, TumorMarkerCreateSchema
from .RiskAssessment import RiskAssessmentSchema, RiskAssessmentCreateSchema
from .SystemicTherapy import (
    SystemicTherapySchema, SystemicTherapyCreateSchema, 
    SystemicTherapyMedicationSchema, SystemicTherapyMedicationCreateSchema,
)
from .Surgery import SurgerySchema, SurgeryCreateSchema 
from .Radiotherapy import (
    RadiotherapySchema, RadiotherapyCreateSchema, 
    RadiotherapyDosageSchema, RadiotherapyDosageCreateSchema,
    RadiotherapySettingSchema, RadiotherapySettingCreateSchema,
)
from .PerformanceStatus import PerformanceStatusSchema, PerformanceStatusCreateSchema
from .AdverseEvent import (
    AdverseEventSchema, AdverseEventCreateSchema,
    AdverseEventSuspectedCauseSchema, AdverseEventSuspectedCauseCreateSchema,
    AdverseEventMitigationSchema, AdverseEventMitigationCreateSchema
)
from .Lifestyle import LifestyleSchema, LifestyleCreateSchema
from .FamilyHistory import FamilyHistorySchema, FamilyHistoryCreateSchema
from .Vitals import VitalsSchema, VitalsCreateSchema
from .TreatmentResponse import TreatmentResponseSchema, TreatmentResponseCreateSchema
from .TumorBoard import (
    UnspecifiedTumorBoardSchema, UnspecifiedTumorBoardCreateSchema,
    MolecularTumorBoardSchema, MolecularTumorBoardCreateSchema,
    MolecularTherapeuticRecommendationSchema, MolecularTherapeuticRecommendationCreateSchema
)
from .Comorbidities import ComorbiditiesAssessmentSchema, ComorbiditiesAssessmentCreateSchema, ComorbiditiesPanelSchema, ComorbidityPanelCategory
from .GenomicVariant import GenomicVariantSchema, GenomicVariantCreateSchema
from .GenomicSignature import (
    TumorMutationalBurdenSchema, TumorMutationalBurdenCreateSchema,
    MicrosatelliteInstabilitySchema, MicrosatelliteInstabilityCreateSchema,
    LossOfHeterozygositySchema, LossOfHeterozygosityCreateSchema,
    HomologousRecombinationDeficiencySchema, HomologousRecombinationDeficiencyCreateSchema,
    TumorNeoantigenBurdenSchema, TumorNeoantigenBurdenCreateSchema,
    AneuploidScoreSchema, AneuploidScoreCreateSchema,
)

# Filter schemas
PatientCaseFilters = create_filters_schema(schema = PatientCaseSchema, name='PatientCaseFilters')
NeoplasticEntityFilters = create_filters_schema(schema = NeoplasticEntitySchema, name='NeoplasticEntityFilters')
TumorMarkerFilters = create_filters_schema(schema = TumorMarkerSchema, name='TumorMarkerFilters')
RiskAssessmentFilters = create_filters_schema(schema = RiskAssessmentSchema, name='RiskAssessmentFilters')
SystemicTherapyFilters = create_filters_schema(schema = SystemicTherapySchema, name='SystemicTherapyFilters')
SurgeryFilters = create_filters_schema(schema = SurgerySchema, name='SurgeryFilters')
RadiotherapyFilters = create_filters_schema(schema = RadiotherapySchema, name='RadiotherapyFilters')
AdverseEventFilters = create_filters_schema(schema = AdverseEventSchema, name='AdverseEventFilters')
TreatmentResponseFilters = create_filters_schema(schema = TreatmentResponseSchema, name='TreatmentResponseFilters')
UnspecifiedTumorBoardFilters = create_filters_schema(schema = UnspecifiedTumorBoardSchema, name='UnspecifiedTumorBoardFilters')
PerformanceStatusFilters = create_filters_schema(schema = PerformanceStatusSchema, name='PerformanceStatusFilters')
LifestyleFilters = create_filters_schema(schema = LifestyleSchema, name='LifestyleFilters')
VitalsFilters = create_filters_schema(schema = VitalsSchema, name='VitalsFilters')
ComorbiditiesAssessmentFilters = create_filters_schema(schema = ComorbiditiesAssessmentSchema, name='ComorbiditiesAssessmentFilters')
GenomicVariantFilters = create_filters_schema(schema = GenomicVariantSchema, name='GenomicVariantFilters')


__all__ = (
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
    ComorbiditiesAssessmentSchema, ComorbiditiesAssessmentCreateSchema, ComorbiditiesPanelSchema, ComorbidityPanelCategory,
    # Genomic variant schemas 
    GenomicVariantSchema, GenomicVariantCreateSchema,
    # Genomic signature schemas
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
    SystemicTherapyFilters,
    SurgeryFilters,
    RadiotherapyFilters,
    AdverseEventFilters,
    TreatmentResponseFilters,
    UnspecifiedTumorBoardFilters,
    PerformanceStatusFilters,
    LifestyleFilters,
    VitalsFilters,
    ComorbiditiesAssessmentFilters,
    GenomicVariantFilters,
)