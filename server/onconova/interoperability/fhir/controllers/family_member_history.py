from ninja_extra import api_controller, route
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.interoperability.fhir.schemas import (
    CancerFamilyMemberHistoryProfile,
)
from onconova.oncology.models import FamilyHistory
from fhircraft.fhir.resources.datatypes.R4.core.operation_outcome import (
    OperationOutcome,
)
from onconova.interoperability.fhir.controllers.base import (
    COMMON_READ_HTTP_ERRORS,
    COMMON_UPDATE_HTTP_ERRORS,
    FhirBaseController,
)


@api_controller(
    "FamilyMemberHistory",
    auth=[XSessionTokenAuth()],
    tags=["Family Member Histories"],
)
class FamilyMemberHistoryController(FhirBaseController):

    @route.get(
        path="{rid}",
        response={
            200: CancerFamilyMemberHistoryProfile,
            **COMMON_READ_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="readFamilyMemberHistory",
        exclude_none=True,
        summary="Read the current state of the resource",
    )
    def read_family_member_history(self, rid: str):
        return self.read_fhir_resource(rid, FamilyHistory)

    @route.put(
        path="{rid}",
        response={
            200: CancerFamilyMemberHistoryProfile
            | OperationOutcome
            | None,
            **COMMON_UPDATE_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateFamilyMemberHistory",
        exclude_none=True,
        summary="Update the current state of the resource",
    )
    def update_family_member_history(
        self,
        rid: str,
        payload: CancerFamilyMemberHistoryProfile,
    ):
        return self.update_fhir_resource(rid, payload)

    @route.delete(
        path="{rid}",
        response={
            204: None,
            404: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteFamilyMemberHistory",
        exclude_none=True,
        summary="Delete the resource so that it no exists (no read, search etc)",
    )
    def delete_family_member_history(self, rid: str):
        return self.delete_fhir_resource(rid, FamilyHistory)

    @route.post(
        path="",
        response={
            200: CancerFamilyMemberHistoryProfile
            | OperationOutcome
            | None,
            400: OperationOutcome,
            409: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="createFamilyMemberHistory",
        exclude_none=True,
        summary="Create a new resource",
    )
    def create_family_member_history(
        self, payload: CancerFamilyMemberHistoryProfile
    ):
        return self.create_fhir_resource(payload)
