from .PatientCase import *
from .NeoplasticEntity import *
from .TreatmentResponse import *
from .Staging import *
from .TumorMarker import *
from .RiskAssessment import *
from .SystemicTherapy import *
from .Surgery import *
from .Radiotherapy import *
from .TherapyLine import *
from .PerformanceStatus import *
from .TumorBoard import *
from .AdverseEvent import *
from .Lifestyle import *
from .FamilyHistory import *
from .Comorbidities import *
from .Vitals import *
from .GenomicVariant import *
from .GenomicSignature import *

MODELS = (
    # Patient case
    PatientCase, PatientCaseDataCompletion,
    # Neoplastic entity    
    NeoplasticEntity,
    # Stagings
    Staging, StagingDomain, TNMStaging, FIGOStaging, BinetStaging, RaiStaging, BreslowDepth, ClarkStaging, ISSStaging,
    RISSStaging, GleasonGrade, INSSStage, INRGSSStage, WilmsStage, RhabdomyosarcomaClinicalGroup, LymphomaStaging,
    # Tumor marker
    TumorMarker,
    # Risk assessment
    RiskAssessment,
    # Treatment Response
    TreatmentResponse,
    # Therapy line
    TherapyLine,
    # Systemic therapy
    SystemicTherapy, SystemicTherapyMedication,
    # Performance status
    PerformanceStatus,
    # Surgery
    Surgery,
    # Radiotherapy
    Radiotherapy, RadiotherapyDosage, RadiotherapySetting,
    # Lifestyle
    Lifestyle,
    # Comorbidities
    ComorbiditiesAssessment, ComorbiditiesPanel, ComorbidityPanelCategory,
    # Family history
    FamilyHistory,
    # Tumor boards
    TumorBoard, MolecularTumorBoard, UnspecifiedTumorBoard, MolecularTherapeuticRecommendation,
    # Adverse events
    AdverseEvent, AdverseEventSuspectedCause, AdverseEventMitigation,
    # Vitals 
    Vitals,
    # Genomic variant
    GenomicVariant,
    # Genomic signatures
    GenomicSignatureTypes,GenomicSignature, TumorMutationalBurden, MicrosatelliteInstability,
    LossOfHeterozygosity, HomologousRecombinationDeficiency, TumorNeoantigenBurden, AneuploidScore,
)

__all__ = [model.__name__ for model in MODELS]