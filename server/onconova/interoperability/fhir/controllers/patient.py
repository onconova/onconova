from django.urls import resolve
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate

from onconova.core.anonymization import anonymize
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.interoperability.fhir.schemas import OnconovaCancerPatient
from onconova.oncology.models import PatientCase


@api_controller(
    "Patient",
    # auth=[XSessionTokenAuth()],
    tags=["Patients"],
)
class PatientController(ControllerBase):

    @route.get(
        path="{rid}",
        response={200: OnconovaCancerPatient, **COMMON_HTTP_ERRORS},
        # permissions=[perms.CanViewCases],
        operation_id="readPatient",
        exclude_none=True,
    )
    def read_patient(self, rid: str):
        return PatientCase.objects.get(id=rid)
