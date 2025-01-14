from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

from pop.core.controllers import AuthController, UsersController, MeasuresController
from pop.terminology.controllers import TerminologyController
from pop.oncology.controllers import (
    PatientCaseController,
    NeoplasticEntityController,
    StagingController,    
    TumorMarkerController,
    RiskAssessmentController,
    SystemicTherapyController,
    SystemicTherapyController,
    SurgeryController,
    RadiotherapyController,
    PerformanceStatusController,
    LifestyleController,
    ComorbiditiesAssessmentController,
    ComorbiditiesPanelsController,
    FamilyHistoryController,
    GenomicVariantController,
    GenomicSignatureController,
)


api = NinjaExtraAPI(
    title="POP API",
    description="Precision Oncology Platform API for exchange of research cancer data",
    urls_namespace="pop",
)
api.register_controllers(
    AuthController,
    UsersController,
    PatientCaseController,
    NeoplasticEntityController,
    StagingController,
    RiskAssessmentController,
    TumorMarkerController,
    SystemicTherapyController,
    SurgeryController,
    RadiotherapyController,
    PerformanceStatusController,
    GenomicVariantController,
    GenomicSignatureController,
    LifestyleController,
    FamilyHistoryController,
    ComorbiditiesAssessmentController,
    ComorbiditiesPanelsController,
    MeasuresController,
    TerminologyController,
)
