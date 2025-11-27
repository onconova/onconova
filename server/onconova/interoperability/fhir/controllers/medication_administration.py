from ninja_extra import api_controller, route
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.interoperability.fhir.schemas import (
    MedicationAdministrationProfile,
)
from onconova.oncology.models import SystemicTherapy
from fhircraft.fhir.resources.datatypes.R4.core.operation_outcome import (
    OperationOutcome,
)
from onconova.interoperability.fhir.controllers.base import (
    COMMON_READ_HTTP_ERRORS,
    COMMON_UPDATE_HTTP_ERRORS,
    FhirBaseController,
)


@api_controller(
    "MedicationAdministration",
    auth=[XSessionTokenAuth()],
    tags=["Medication Administrations"],
)
class MedicationAdministrationController(FhirBaseController):

    @route.get(
        path="{rid}",
        response={
            200: MedicationAdministrationProfile,
            **COMMON_READ_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="readMedicationAdministration",
        exclude_none=True,
        summary="Read the current state of the resource",
    )
    def read_medication_administration(self, rid: str):
        return self.read_fhir_resource(rid, SystemicTherapy)

    @route.put(
        path="{rid}",
        response={
            200: MedicationAdministrationProfile
            | OperationOutcome
            | None,
            **COMMON_UPDATE_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateMedicationAdministration",
        exclude_none=True,
        summary="Update the current state of the resource",
    )
    def update_medication_administration(
        self,
        rid: str,
        payload: MedicationAdministrationProfile,
    ):
        return self.update_fhir_resource(rid, payload)

    @route.delete(
        path="{rid}",
        response={
            204: None,
            404: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteMedicationAdministration",
        exclude_none=True,
        summary="Delete the resource so that it no exists (no read, search etc)",
    )
    def delete_medication_administration(self, rid: str):
        return self.delete_fhir_resource(rid, SystemicTherapy)

    @route.post(
        path="",
        response={
            200: MedicationAdministrationProfile
            | OperationOutcome
            | None,
            400: OperationOutcome,
            409: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="createMedicationAdministration",
        exclude_none=True,
        summary="Create a new resource",
    )
    def create_medication_administration(
        self, payload: MedicationAdministrationProfile
    ):
        return self.create_fhir_resource(payload)
