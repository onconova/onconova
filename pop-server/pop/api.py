from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

from pop.core.controllers import AuthController, UsersController, MeasuresController
from pop.terminology.controllers import TerminologyController
from pop.oncology.controllers import (
    PatientCaseController,
    NeoplasticEntityController,
    StagingController,    
    TumorMarkerController,
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
    TumorMarkerController,
    MeasuresController,
    TerminologyController,
)
