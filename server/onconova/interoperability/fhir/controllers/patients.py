from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate

from onconova.core.anonymization import anonymize
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.oncology.models import (
    PatientCase,
)
from onconova.interoperability.fhir.models import CancerPatient
from django.urls import resolve

from onconova.oncology import schemas

@api_controller(
    "Patient",
    auth=[XSessionTokenAuth()],
    tags=["Patients"],
)
class PatientController(ControllerBase):

    @route.get(
        path="",
        response={200: Paginated[CancerPatient], **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getPatientCases",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_patients(self): 
        return PatientCase.objects.all()
