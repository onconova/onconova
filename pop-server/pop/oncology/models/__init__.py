from .patient_case import *
from .neoplastic_entity import *
from .treatment_response import *
from .staging import *
from .tumor_marker import *
from .risk_assessment import *
from .systemic_therapy import *
from .surgery import *
from .radiotherapy import *
from .therapy_line import *
from .performance_status import *
from .tumor_board import *
from .adverse_event import *
from .lifestyle import *
from .family_history import *
from .comorbidities import *
from .vitals import *
from .genomic_variant import *
from .genomic_signature import *

MODELS = (
    # Patient case
    PatientCase,
    PatientCaseDataCompletion,
    # Neoplastic entity
    NeoplasticEntity,
    # Stagings
    Staging,
    TNMStaging,
    FIGOStaging,
    BinetStaging,
    RaiStaging,
    BreslowDepth,
    ClarkStaging,
    ISSStaging,
    RISSStaging,
    GleasonGrade,
    INSSStage,
    INRGSSStage,
    WilmsStage,
    RhabdomyosarcomaClinicalGroup,
    LymphomaStaging,
    # Tumor marker
    TumorMarker,
    # Risk assessment
    RiskAssessment,
    # Treatment Response
    TreatmentResponse,
    # Therapy line
    TherapyLine,
    # Systemic therapy
    SystemicTherapy,
    SystemicTherapyMedication,
    # Performance status
    PerformanceStatus,
    # Surgery
    Surgery,
    # Radiotherapy
    Radiotherapy,
    RadiotherapyDosage,
    RadiotherapySetting,
    # Lifestyle
    Lifestyle,
    # Comorbidities
    ComorbiditiesAssessment,
    # Family history
    FamilyHistory,
    # Tumor boards
    TumorBoard,
    MolecularTumorBoard,
    UnspecifiedTumorBoard,
    MolecularTherapeuticRecommendation,
    # Adverse events
    AdverseEvent,
    AdverseEventSuspectedCause,
    AdverseEventMitigation,
    # Vitals
    Vitals,
    # Genomic variant
    GenomicVariant,
    # Genomic signatures
    GenomicSignature,
    TumorMutationalBurden,
    MicrosatelliteInstability,
    LossOfHeterozygosity,
    HomologousRecombinationDeficiency,
    TumorNeoantigenBurden,
    AneuploidScore,
)

__all__ = [model.__name__ for model in MODELS]
