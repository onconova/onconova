from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate
from django.shortcuts import get_object_or_404

from onconova.core.anonymization import anonymize
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.oncology.models import (
    PatientCase,
)
from onconova.interoperability.fhir.schemas import CancerPatient


from onconova.oncology import schemas

@api_controller(
    "Patient/{id}",
    auth=None,
    tags=["Patients"],
)
class PatientController(ControllerBase):

    @route.get(
        path="",
        response={200: CancerPatient, **COMMON_HTTP_ERRORS},
        permissions=None,
        operation_id="readPatient",
        exclude_none=True,
    )
    def read_patient(self, id: str): 
        return CancerPatient.model_validate(
            get_object_or_404(PatientCase, id=id)
        )
