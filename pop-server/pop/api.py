from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

from pop.core.controllers import AuthController
from pop.terminology.controllers import TerminologyController
from pop.oncology.controllers import (
    PatientCaseController,
)
api = NinjaExtraAPI(
    title="POP API",
    description="Precision Oncology Platform API for exchange of research cancer data",
    urls_namespace="pop",
)
api.register_controllers(
    AuthController,
    PatientCaseController,
    TerminologyController,
)
