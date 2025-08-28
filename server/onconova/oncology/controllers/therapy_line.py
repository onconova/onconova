from typing import List

import pghistory
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja.schema import Field, Schema
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate

from onconova.core.anonymization import anonymize
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.history.schemas import HistoryEvent
from onconova.core.schemas import ModifiedResource as ModifiedResourceSchema
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.oncology.models import PatientCase, TherapyLine
from onconova.oncology.schemas import (
    TherapyLineCreateSchema,
    TherapyLineFilters,
    TherapyLineSchema,
)


@api_controller(
    "therapy-lines",
    auth=[XSessionTokenAuth()],
    tags=["Therapy Lines"],
)
class TherapyLineController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[TherapyLineSchema],
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getTherapyLines",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_therapy_lines_matching_the_query(self, query: Query[TherapyLineFilters]):  # type: ignore
        queryset = TherapyLine.objects.all().order_by("-period")
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createTherapyLine",
    )
    def create_therapy_line(self, payload: TherapyLineCreateSchema):  # type: ignore
        return 201, payload.model_dump_django()

    @route.get(
        path="/{therapyLineId}",
        response={200: TherapyLineSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getTherapyLineById",
    )
    @anonymize()
    def get_therapy_line_by_id(self, therapyLineId: str):
        return get_object_or_404(TherapyLine, id=therapyLineId)

    @route.put(
        path="/{therapyLineId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateTherapyLine",
    )
    def update_therapy_line(self, therapyLineId: str, payload: TherapyLineCreateSchema):  # type: ignore
        instance = get_object_or_404(TherapyLine, id=therapyLineId)
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{therapyLineId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteTherapyLine",
    )
    def delete_therapy_line(self, therapyLineId: str):
        get_object_or_404(TherapyLine, id=therapyLineId).delete()
        return 204, None

    @route.get(
        path="/{therapyLineId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(TherapyLineCreateSchema)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllTherapyLineHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_therapy_line_history_events(self, therapyLineId: str):
        instance = get_object_or_404(TherapyLine, id=therapyLineId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{therapyLineId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(TherapyLineCreateSchema),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getTherapyLineHistoryEventById",
    )
    def get_therapy_line_history_event_by_id(self, therapyLineId: str, eventId: str):
        instance = get_object_or_404(TherapyLine, id=therapyLineId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{therapyLineId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertTherapyLineToHistoryEvent",
    )
    def revert_therapy_line_to_history_event(self, therapyLineId: str, eventId: str):
        instance = get_object_or_404(TherapyLine, id=therapyLineId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.get(
        path="/{caseId}/re-assignments",
        response={200: List[TherapyLineSchema], 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getReassignedPatientCaseTherapyLines",
    )
    def get_reassigned_patient_case_therapy_lines(self, caseId: str):
        return TherapyLine.assign_therapy_lines(
            get_object_or_404(PatientCase, id=caseId)
        )
