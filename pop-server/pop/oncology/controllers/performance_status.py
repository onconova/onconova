import pghistory

from ninja import Query
from ninja.schema import Schema, Field
from ninja_extra.pagination import paginate
from ninja_extra.ordering import ordering
from ninja_extra import api_controller, ControllerBase, route

from pop.core.auth import permissions as perms
from pop.core.anonymization import anonymize
from pop.core.auth.token import XSessionTokenAuth
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema, Paginated
from pop.core.history.schemas import HistoryEvent
from pop.oncology.models import PerformanceStatus

from django.shortcuts import get_object_or_404
from pop.oncology.schemas import (
    PerformanceStatusSchema,
    PerformanceStatusCreateSchema,
    PerformanceStatusFilters,
)


@api_controller(
    "performance-status",
    auth=[XSessionTokenAuth()],
    tags=["Performance Status"],
)
class PerformanceStatusController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[PerformanceStatusSchema],
        },
        permissions=[perms.CanViewCases],
        operation_id="getPerformanceStatus",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_performance_status_matching_the_query(self, query: Query[PerformanceStatusFilters], anonymized: bool = True):  # type: ignore
        queryset = PerformanceStatus.objects.all().order_by("-date")
        return query.filter(queryset)

    @route.post(
        path="",
        response={
            201: ModifiedResourceSchema,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="createPerformanceStatus",
    )
    def create_performance_status(self, payload: PerformanceStatusCreateSchema):  # type: ignore
        return 201, payload.model_dump_django()

    @route.get(
        path="/{performanceStatusId}",
        response={
            200: PerformanceStatusSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getPerformanceStatusById",
    )
    @anonymize()
    def get_performance_status_by_id(
        self, performanceStatusId: str, anonymized: bool = True
    ):
        return get_object_or_404(PerformanceStatus, id=performanceStatusId)

    @route.put(
        path="/{performanceStatusId}",
        response={
            200: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="updatePerformanceStatusById",
    )
    def update_performance_status(self, performanceStatusId: str, payload: PerformanceStatusCreateSchema):  # type: ignore
        instance = get_object_or_404(PerformanceStatus, id=performanceStatusId)
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{performanceStatusId}",
        response={
            204: None,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="deletePerformanceStatus",
    )
    def delete_performance_status(self, performanceStatusId: str):
        get_object_or_404(PerformanceStatus, id=performanceStatusId).delete()
        return 204, None

    @route.get(
        path="/{performanceStatusId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(PerformanceStatusCreateSchema)],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllPerformanceStatusHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_performance_status_history_events(self, performanceStatusId: str):
        instance = get_object_or_404(PerformanceStatus, id=performanceStatusId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{performanceStatusId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(PerformanceStatusCreateSchema),
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getPerformanceStatusHistoryEventById",
    )
    def get_performance_status_history_event_by_id(
        self, performanceStatusId: str, eventId: str
    ):
        instance = get_object_or_404(PerformanceStatus, id=performanceStatusId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{performanceStatusId}/history/events/{eventId}/reversion",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="revertPerformanceStatusToHistoryEvent",
    )
    def revert_performance_status_to_history_event(
        self, performanceStatusId: str, eventId: str
    ):
        instance = get_object_or_404(PerformanceStatus, id=performanceStatusId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
