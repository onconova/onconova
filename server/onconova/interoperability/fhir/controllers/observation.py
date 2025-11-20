from ninja_extra import api_controller, route
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.interoperability.fhir.schemas import (
    TumorMarkerProfile,
)
from onconova.oncology.models import TumorMarker
from fhircraft.fhir.resources.datatypes.R4.core.operation_outcome import (
    OperationOutcome,
)
from onconova.interoperability.fhir.controllers.base import (
    COMMON_READ_HTTP_ERRORS,
    COMMON_UPDATE_HTTP_ERRORS,
    FhirBaseController,
)


@api_controller(
    "Observation",
    auth=[XSessionTokenAuth()],
    tags=["Observations"],
)
class ObservationController(FhirBaseController):

    @route.get(
        path="{rid}",
        response={
            200: TumorMarkerProfile,
            **COMMON_READ_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="readObservation",
        exclude_none=True,
    )
    def read_observation(self, rid: str):
        return self.read_fhir_resource(rid, TumorMarker)

    @route.put(
        path="{rid}",
        response={
            200: TumorMarkerProfile
            | OperationOutcome
            | None,
            **COMMON_UPDATE_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateObservation",
        exclude_none=True,
    )
    def update_observation(
        self,
        rid: str,
        payload: TumorMarkerProfile,
    ):
        if isinstance(payload, TumorMarkerProfile):
            return self.update_fhir_resource(rid, TumorMarker, payload)

    @route.delete(
        path="{rid}",
        response={
            204: None,
            404: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteObservation",
        exclude_none=True,
    )
    def delete_observation(self, rid: str):
        return self.delete_fhir_resource(rid, TumorMarker)

    @route.post(
        path="",
        response={
            200: TumorMarkerProfile
            | OperationOutcome
            | None,
            400: OperationOutcome,
            409: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="createObservation",
        exclude_none=True,
    )
    def create_observation(
        self, payload: TumorMarkerProfile
    ):
        return self.create_fhir_resource(payload)
