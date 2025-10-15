import pghistory
from django.shortcuts import get_object_or_404
from ninja import Query
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
import onconova.oncology.models as orm 
import onconova.oncology.schemas as scm


@api_controller(
    "performance-status",
    auth=[XSessionTokenAuth()],
    tags=["Performance Status"],
)
class PerformanceStatusController(ControllerBase):

    @route.get(
        path="",
        response={200: Paginated[scm.PerformanceStatus], **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getPerformanceStatus",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_performance_status_matching_the_query(self, query: Query[scm.PerformanceStatusFilters]):  # type: ignore
        queryset = orm.PerformanceStatus.objects.all().order_by("-date")
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createPerformanceStatus",
    )
    def create_performance_status(self, payload: scm.PerformanceStatusCreate):
        return 201, payload.model_dump_django()

    @route.get(
        path="/{performanceStatusId}",
        response={200: scm.PerformanceStatus, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getPerformanceStatusById",
    )
    @anonymize()
    def get_performance_status_by_id(self, performanceStatusId: str):
        return get_object_or_404(orm.PerformanceStatus, id=performanceStatusId)

    @route.put(
        path="/{performanceStatusId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updatePerformanceStatusById",
    )
    def update_performance_status(self, performanceStatusId: str, payload: scm.PerformanceStatusCreate): 
        instance = get_object_or_404(orm.PerformanceStatus, id=performanceStatusId)
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{performanceStatusId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deletePerformanceStatus",
    )
    def delete_performance_status(self, performanceStatusId: str):
        get_object_or_404(orm.PerformanceStatus, id=performanceStatusId).delete()
        return 204, None

    @route.get(
        path="/{performanceStatusId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(scm.PerformanceStatusCreate)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllPerformanceStatusHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_performance_status_history_events(self, performanceStatusId: str):
        instance = get_object_or_404(orm.PerformanceStatus, id=performanceStatusId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{performanceStatusId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.PerformanceStatusCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getPerformanceStatusHistoryEventById",
    )
    def get_performance_status_history_event_by_id(
        self, performanceStatusId: str, eventId: str
    ):
        instance = get_object_or_404(orm.PerformanceStatus, id=performanceStatusId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{performanceStatusId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertPerformanceStatusToHistoryEvent",
    )
    def revert_performance_status_to_history_event(
        self, performanceStatusId: str, eventId: str
    ):
        instance = get_object_or_404(orm.PerformanceStatus, id=performanceStatusId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
