from ninja_extra import api_controller, route
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.interoperability.fhir.schemas import (
    TherapyLineProfile,
)
from onconova.oncology.models import TherapyLine
from fhircraft.fhir.resources.datatypes.R4.core.operation_outcome import (
    OperationOutcome,
)
from onconova.interoperability.fhir.controllers.base import (
    COMMON_READ_HTTP_ERRORS,
    COMMON_UPDATE_HTTP_ERRORS,
    FhirBaseController,
)


@api_controller(
    "EpisodeOfCare",
    auth=[XSessionTokenAuth()],
    tags=["Episode Of Care"],
)
class EpisodeOfCareController(FhirBaseController):

    @route.get(
        path="{rid}",
        response={
            200: TherapyLineProfile,
            **COMMON_READ_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="readEpisodeOfCare",
        exclude_none=True,
        summary="Read the current state of the resource",
    )
    def read_episode_of_care(self, rid: str):
        return self.read_fhir_resource(rid, TherapyLine)

    @route.put(
        path="{rid}",
        response={
            200: TherapyLineProfile | OperationOutcome | None,
            **COMMON_UPDATE_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateEpisodeOfCare",
        exclude_none=True,
        summary="Update the current state of the resource",
    )
    def update_episode_of_care(
        self,
        rid: str,
        payload: TherapyLineProfile,
    ):
        return self.update_fhir_resource(rid, payload)

    @route.delete(
        path="{rid}",
        response={
            204: None,
            404: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteEpisodeOfCare",
        exclude_none=True,
        summary="Delete the resource so that it no exists (no read, search etc)",
    )
    def delete_episode_of_care(self, rid: str):
        return self.delete_fhir_resource(rid, TherapyLine)

    @route.post(
        path="",
        response={
            200: TherapyLineProfile | OperationOutcome | None,
            400: OperationOutcome,
            409: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="createEpisodeOfCare",
        exclude_none=True,
        summary="Create a new resource",
    )
    def create_episode_of_care(self, payload: TherapyLineProfile):
        return self.create_fhir_resource(payload)
