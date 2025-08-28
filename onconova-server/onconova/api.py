from ninja import Redoc
from ninja_extra import NinjaExtraAPI

from onconova.analytics.controllers import DashboardController
from onconova.core.auth.controllers import AuthController, UsersController
from onconova.core.healthcheck import HealthCheckController
from onconova.core.measures.controllers import MeasuresController
from onconova.interoperability.controllers import InteroperabilityController
from onconova.oncology.controllers import (
    AdverseEventController,
    ComorbiditiesAssessmentController,
    FamilyHistoryController,
    GenePanelController,
    GenomicSignatureController,
    GenomicVariantController,
    LifestyleController,
    MolecularTherapeuticRecommendationController,
    NeoplasticEntityController,
    OthersController,
    PatientCaseController,
    PerformanceStatusController,
    RadiotherapyController,
    RiskAssessmentController,
    StagingController,
    SurgeryController,
    SystemicTherapyController,
    TherapyLineController,
    TreatmentResponseController,
    TumorBoardController,
    TumorMarkerController,
    VitalsController,
)
from onconova.research.controllers.analysis import CohortAnalysisController
from onconova.research.controllers.cohort import CohortsController
from onconova.research.controllers.dataset import DatasetsController
from onconova.research.controllers.project import ProjectController
from onconova.terminology.controllers import TerminologyController

api = NinjaExtraAPI(
    title="Onconova API",
    description="""
Welcome to the Precision Oncology Platform API — a secure, standards-based interface designed to facilitate the exchange, management, and 
analysis of research data related to cancer genomics, clinical records, and associated metadata. This API provides an extensive set of RESTful endpoints enabling authorized users to perform full CRUD (Create, Read, Update, Delete) operations on various resources within the platform’s data ecosystem.

The primary objective of this API is to support precision oncology research by enabling interoperability between data systems, promoting data sharing among research institutions, and streamlining workflows for clinical and genomic data management in a secure, authenticated environment.

### Authentication
To ensure the security and integrity of cancer research data, **all API requests require proper authentication**.

A valid session token must be obtained prior to accessing any protected endpoint. This token must be included in the request header `X-Session-Token`.

The authentication and authorization flows for obtaining and managing session tokens are provided through the AllAuth authentication service. 
This includes endpoints for user login, logout, password management, and token renewal. For complete details on implementing authentication and 
managing session tokens, please refer to the [AllAuth API documentation](/api/allauth/openapi.html).

**Important:** Unauthorized requests or those missing valid authentication tokens will receive an `HTTP 401 Unauthorized` response.

### Terminologies 
Many resources take objects of the type `CodedConcept` to represent concepts from coded terminologies. Each property of the type `CodedConcept` in a schema will have an associated `x-terminology` attribute. The full list of `CodedConcept` objects allowed for specific resource properties can be retrieved through the [terminology endpoint](#tag/Terminology/operation/getTerminologyConcepts) by passing the `x-terminology` value as the `terminologyName` parameter. 

### Terms and Conditions
By accessing and using this website, you agree to comply with and be bound by the following terms and conditions. The content provided on this API is 
intended solely for general informational and research purposes. While we strive to ensure the information is accurate and reliable, we do not make 
any express or implied warranties about the accuracy, adequacy, validity, reliability, availability, or completeness of the content.

The information presented on this platform is provided in good faith. However, we do not accept any liability for any loss or damage incurred as a 
result of using the site or relying on the information provided. Your use of this site and any reliance on the content is solely at your own risk.

These terms and conditions may be updated from time to time, and it is your responsibility to review them regularly to ensure compliance.

### License 
The Precision Oncology Platform API specification is made available under the MIT License, a permissive open-source license that allows users to freely use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the inclusion of the original copyright and license.
    """,
    urls_namespace="onconova",
    servers=[
        dict(
            url="https://{domain}:{port}/api",
            description="API server",
            variables={"port": {"default": "4443"}, "domain": {"default": "localhost"}},
        ),
    ],
    openapi_extra=dict(
        info=dict(
            license=dict(
                name="MIT",
                url="https://github.com/precisionmedicineinitiative/ONCONOVA/blob/main/LICENSE",
            )
        )
    ),
    docs=Redoc(
        settings={
            "showExtensions": ["x-terminology", "x-measure", "x-default-unit"],
            "generateCodeSamples": {"languages": [{"lang": "curl"}]},
        }
    ),
)
api.register_controllers(
    HealthCheckController,
    AuthController,
    UsersController,
    ProjectController,
    InteroperabilityController,
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
    GenePanelController,
    GenomicSignatureController,
    LifestyleController,
    FamilyHistoryController,
    ComorbiditiesAssessmentController,
    VitalsController,
    MeasuresController,
    TerminologyController,
    CohortsController,
    CohortAnalysisController,
    DashboardController,
    DatasetsController,
    OthersController,
)
