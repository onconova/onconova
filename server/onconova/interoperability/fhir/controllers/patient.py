from ninja_extra import api_controller, route
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.interoperability.fhir.schemas import CancerPatientProfile
from onconova.oncology.models import PatientCase
from fhircraft.fhir.resources.datatypes.R4.core.operation_outcome import (
    OperationOutcome,
)
from onconova.interoperability.fhir.controllers.base import (
    COMMON_READ_HTTP_ERRORS,
    COMMON_UPDATE_HTTP_ERRORS,
    FhirBaseController,
)


@api_controller(
    "Patient",
    auth=[XSessionTokenAuth()],
    tags=["Patients"],
)
class PatientController(FhirBaseController):

    @route.get(
        path="{rid}",
        response={200: CancerPatientProfile, **COMMON_READ_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="readPatient",
        exclude_none=True,
    )
    def read_patient(self, rid: str):
        return self.read_fhir_resource(rid, PatientCase)

    @route.put(
        path="{rid}",
        response={
            200: CancerPatientProfile | OperationOutcome | None,
            **COMMON_UPDATE_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="updatePatient",
        exclude_none=True,
    )
    def update_patient(self, rid: str, payload: CancerPatientProfile):
        return self.update_fhir_resource(rid, payload)

    @route.delete(
        path="{rid}",
        response={
            204: None,
            404: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="deletePatient",
        exclude_none=True,
    )
    def delete_patient(self, rid: str):
        return self.delete_fhir_resource(rid, PatientCase)

    @route.post(
        path="",
        response={
            200: CancerPatientProfile | OperationOutcome | None,
            400: OperationOutcome,
            409: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="createPatient",
        exclude_none=True,
    )
    def create_patient(self, payload: CancerPatientProfile):
        return self.create_fhir_resource(payload)
