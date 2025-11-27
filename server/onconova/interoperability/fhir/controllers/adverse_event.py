from ninja_extra import api_controller, route
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.interoperability.fhir.schemas import (
    AdverseEventProfile,
)
from onconova.oncology.models import AdverseEvent
from fhircraft.fhir.resources.datatypes.R4.core.operation_outcome import (
    OperationOutcome,
)
from onconova.interoperability.fhir.controllers.base import (
    COMMON_READ_HTTP_ERRORS,
    COMMON_UPDATE_HTTP_ERRORS,
    FhirBaseController,
)


@api_controller(
    "AdverseEvent",
    auth=[XSessionTokenAuth()],
    tags=["Adverse Events"],
)
class AdverseEventController(FhirBaseController):

    @route.get(
        path="{rid}",
        response={
            200: AdverseEventProfile,
            **COMMON_READ_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="readAdverseEvent",
        exclude_none=True,
        summary="Read the current state of the resource",
    )
    def read_adverse_event(self, rid: str):
        return self.read_fhir_resource(rid, AdverseEvent)

    @route.put(
        path="{rid}",
        response={
            200: AdverseEventProfile
            | OperationOutcome
            | None,
            **COMMON_UPDATE_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateAdverseEvent",
        exclude_none=True,
        summary="Update the current state of the resource",
    )
    def update_adverse_event(
        self,
        rid: str,
        payload: AdverseEventProfile,
    ):
        return self.update_fhir_resource(rid, payload)

    @route.delete(
        path="{rid}",
        response={
            204: None,
            404: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteAdverseEvent",
        exclude_none=True,
        summary="Delete the resource so that it no exists (no read, search etc)",
    )
    def delete_adverse_event(self, rid: str):
        return self.delete_fhir_resource(rid, AdverseEvent)

    @route.post(
        path="",
        response={
            200: AdverseEventProfile
            | OperationOutcome
            | None,
            400: OperationOutcome,
            409: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="createAdverseEvent",
        exclude_none=True,
        summary="Create a new resource",
    )
    def create_adverse_event(
        self, payload: AdverseEventProfile
    ):
        return self.create_fhir_resource(payload)
