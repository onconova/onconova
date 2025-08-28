from .patient_case import PatientCase, PatientCaseDataCompletion
from .neoplastic_entity import NeoplasticEntity
from .treatment_response import TreatmentResponse
from .systemic_therapy import SystemicTherapy, SystemicTherapyMedication
from .radiotherapy import Radiotherapy, RadiotherapyDosage, RadiotherapySetting
from .surgery import Surgery
from .therapy_line import TherapyLine
from .adverse_event import (
    AdverseEvent,
    AdverseEventMitigation,
    AdverseEventSuspectedCause,
)
from .comorbidities import ComorbiditiesAssessment
from .family_history import FamilyHistory
from .genomic_signature import (
    AneuploidScore,
    GenomicSignature,
    HomologousRecombinationDeficiency,
    LossOfHeterozygosity,
    MicrosatelliteInstability,
    TumorMutationalBurden,
    TumorNeoantigenBurden,
)
from .genomic_variant import GenomicVariant
from .lifestyle import Lifestyle
from .performance_status import PerformanceStatus
from .risk_assessment import RiskAssessment
from .staging import (
    BinetStaging,
    BreslowDepth,
    ClarkStaging,
    FIGOStaging,
    GleasonGrade,
    INRGSSStage,
    INSSStage,
    ISSStaging,
    LymphomaStaging,
    RaiStaging,
    RhabdomyosarcomaClinicalGroup,
    RISSStaging,
    Staging,
    TNMStaging,
    WilmsStage,
)
from .tumor_board import (
    MolecularTherapeuticRecommendation,
    MolecularTumorBoard,
    TumorBoard,
    UnspecifiedTumorBoard,
)
from .tumor_marker import TumorMarker
from .vitals import Vitals

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

__all__ = [
    "PatientCase",
    "PatientCaseDataCompletion",
    "NeoplasticEntity",
    "Staging",
    "TNMStaging",
    "FIGOStaging",
    "BinetStaging",
    "RaiStaging",
    "BreslowDepth",
    "ClarkStaging",
    "ISSStaging",
    "RISSStaging",
    "GleasonGrade",
    "INSSStage",
    "INRGSSStage",
    "WilmsStage",
    "RhabdomyosarcomaClinicalGroup",
    "LymphomaStaging",
    "TumorMarker",
    "RiskAssessment",
    "TreatmentResponse",
    "TherapyLine",
    "SystemicTherapy",
    "SystemicTherapyMedication",
    "PerformanceStatus",
    "Surgery",
    "Radiotherapy",
    "RadiotherapyDosage",
    "RadiotherapySetting",
    "Lifestyle",
    "ComorbiditiesAssessment",
    "FamilyHistory",
    "TumorBoard",
    "MolecularTumorBoard",
    "UnspecifiedTumorBoard",
    "MolecularTherapeuticRecommendation",
    "AdverseEvent",
    "AdverseEventSuspectedCause",
    "AdverseEventMitigation",
    "Vitals",
    "GenomicVariant",
    "GenomicSignature",
    "TumorMutationalBurden",
    "MicrosatelliteInstability",
    "LossOfHeterozygosity",
    "HomologousRecombinationDeficiency",
    "TumorNeoantigenBurden",
    "AneuploidScore",
]
