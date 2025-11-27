from ninja_extra import api_controller, route
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.interoperability.fhir.schemas import (
    SurgicalProcedureProfile,
    RadiotherapyCourseSummaryProfile,
    TumorBoardReviewProfile,
    MolecularTumorBoardReviewProfile,
)
from onconova.oncology.models import (
    Surgery,
    Radiotherapy,
    UnspecifiedTumorBoard,
    MolecularTumorBoard,
)
from fhircraft.fhir.resources.datatypes.R4.core.operation_outcome import (
    OperationOutcome,
)
from onconova.interoperability.fhir.controllers.base import (
    COMMON_READ_HTTP_ERRORS,
    COMMON_UPDATE_HTTP_ERRORS,
    FhirBaseController,
)


@api_controller(
    "Procedure",
    auth=[XSessionTokenAuth()],
    tags=["Procedures"],
)
class ProcedureController(FhirBaseController):

    @route.get(
        path="{rid}",
        response={
            200: RadiotherapyCourseSummaryProfile
            | SurgicalProcedureProfile
            | MolecularTumorBoardReviewProfile
            | TumorBoardReviewProfile,
            **COMMON_READ_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="readProcedure",
        exclude_none=True,
        summary="Read the current state of the resource",
    )
    def read_procedure(self, rid: str):
        return self.read_fhir_resource(rid, [
            Surgery, 
            Radiotherapy,
            UnspecifiedTumorBoard,
            MolecularTumorBoard,
        ])

    @route.put(
        path="{rid}",
        response={
            200: RadiotherapyCourseSummaryProfile
            | SurgicalProcedureProfile
            | MolecularTumorBoardReviewProfile
            | TumorBoardReviewProfile
            | OperationOutcome
            | None,
            **COMMON_UPDATE_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateProcedure",
        exclude_none=True,
        summary="Update the current state of the resource",
    )
    def update_procedure(
        self,
        rid: str,
        payload: RadiotherapyCourseSummaryProfile
            | SurgicalProcedureProfile
            | MolecularTumorBoardReviewProfile
            | TumorBoardReviewProfile,
    ):
        return self.update_fhir_resource(rid, payload)

    @route.delete(
        path="{rid}",
        response={
            204: None,
            404: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteProcedure",
        exclude_none=True,
        summary="Delete the resource so that it no exists (no read, search etc)",
    )
    def delete_procedure(self, rid: str):
        return self.delete_fhir_resource(rid, [
            Surgery,
            Radiotherapy, 
            UnspecifiedTumorBoard,
            MolecularTumorBoard,
        ])

    @route.post(
        path="",
        response={
            200: RadiotherapyCourseSummaryProfile
            | SurgicalProcedureProfile
            | MolecularTumorBoardReviewProfile
            | TumorBoardReviewProfile
            | OperationOutcome
            | None,
            400: OperationOutcome,
            409: OperationOutcome,
        },
        permissions=[perms.CanManageCases],
        operation_id="createProcedure",
        exclude_none=True,
        summary="Create a new resource",
    )
    def create_procedure(
        self, payload: RadiotherapyCourseSummaryProfile
            | SurgicalProcedureProfile
            | MolecularTumorBoardReviewProfile
            | TumorBoardReviewProfile
    ):
        return self.create_fhir_resource(payload)
