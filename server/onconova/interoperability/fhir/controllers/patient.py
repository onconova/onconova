from ninja_extra import api_controller, route
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.interoperability.fhir.schemas import CancerPatientProfile, BundleProfile
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
        summary="Read the current state of the resource",
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
        summary="Update the current state of the resource",
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
        summary="Delete the resource so that it no exists (no read, search etc)",
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
        summary="Create a new resource",
    )
    def create_patient(self, payload: CancerPatientProfile):
        return self.create_fhir_resource(payload)

    @route.get(
        path="{rid}/$mcode-everything",
        response={200: BundleProfile, **COMMON_READ_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="FetchmCODEPatientBundle",
        exclude_none=True,
        summary="Read the current state of the resource",
    )
    def fetch_mcode_patient_bundle(self, rid: str):
        if not (instance := PatientCase.objects.filter(id=rid).first()):
            # If resource not found, check if it was deleted
            if PatientCase.pgh_event_model.objects.filter(pgh_obj_id=rid, pgh_label="delete").exists():  # type: ignore
                return 410, None
            else:
                return 404, None
        # Set the Last-Modified header if the instance has an updated_at timestamp
        if getattr(instance, "updated_at", None):
            assert self.context and self.context.response
            self.context.response.headers["Last-Modified"] = instance.updated_at.isoformat()  # type: ignore
        return BundleProfile.construct_bundle(instance)
