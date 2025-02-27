from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

from django.conf import settings 

from pop.core.controllers import AuthController, UsersController
from pop.core.measures.controllers import MeasuresController
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
    TherapyLineController,
    RadiotherapyController,
    PerformanceStatusController,
    LifestyleController,
    ComorbiditiesAssessmentController,
    ComorbiditiesPanelsController,
    FamilyHistoryController,
    VitalsController,
    GenomicVariantController,
    GenomicSignatureController,
    AdverseEventController,
    TreatmentResponseController,
    TumorBoardController,
    MolecularTherapeuticRecommendationController,
)
from pop.analytics.controllers import (
    CohortsController, 
    CohortBuilderController, 
    DashboardController, 
    DatasetsController,
    CohortAnalysisController
)



api = NinjaExtraAPI(
    title="POP API",
    description="Precision Oncology Platform API for exchange of research cancer data",
    urls_namespace="pop",
    servers=[]
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
    TherapyLineController,
    AdverseEventController,
    TreatmentResponseController,
    TumorBoardController,
    MolecularTherapeuticRecommendationController,
    PerformanceStatusController,
    GenomicVariantController,
    GenomicSignatureController,
    LifestyleController,
    FamilyHistoryController,
    ComorbiditiesAssessmentController,
    ComorbiditiesPanelsController,
    VitalsController,
    MeasuresController,
    TerminologyController,
    CohortsController,
    CohortAnalysisController,
    CohortBuilderController,
    DashboardController,
    DatasetsController,
)
