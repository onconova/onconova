import pghistory
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate
from pop.core.anonymization import anonymize
from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth
from pop.core.history.schemas import HistoryEvent
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema
from pop.core.schemas import Paginated
from pop.core.utils import COMMON_HTTP_ERRORS
from pop.oncology.models import Vitals
from pop.oncology.schemas import VitalsCreateSchema, VitalsFilters, VitalsSchema


@api_controller(
    "vitals",
    auth=[XSessionTokenAuth()],
    tags=["Vitals"],
)
class VitalsController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[VitalsSchema],
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getVitals",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_vitals_matching_the_query(self, query: Query[VitalsFilters]):  # type: ignore
        queryset = Vitals.objects.all().order_by("-date")
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createVitals",
    )
    def create_vitals(self, payload: VitalsCreateSchema):  # type: ignore
        return 201, payload.model_dump_django()

    @route.get(
        path="/{vitalsId}",
        response={200: VitalsSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getVitalsById",
    )
    @anonymize()
    def get_vitals_by_id(self, vitalsId: str):
        return get_object_or_404(Vitals, id=vitalsId)

    @route.put(
        path="/{vitalsId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateVitalsById",
    )
    def update_vitals(self, vitalsId: str, payload: VitalsCreateSchema):  # type: ignore
        instance = get_object_or_404(Vitals, id=vitalsId)
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{vitalsId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteVitalsById",
    )
    def delete_vitals(self, vitalsId: str):
        get_object_or_404(Vitals, id=vitalsId).delete()
        return 204, None

    @route.get(
        path="/{vitalsId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(VitalsCreateSchema)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllVitalsHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_vitals_history_events(self, vitalsId: str):
        instance = get_object_or_404(Vitals, id=vitalsId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{vitalsId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(VitalsCreateSchema),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getVitalsHistoryEventById",
    )
    def get_vitals_history_event_by_id(self, vitalsId: str, eventId: str):
        instance = get_object_or_404(Vitals, id=vitalsId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{vitalsId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertVitalsToHistoryEvent",
    )
    def revert_vitals_to_history_event(self, vitalsId: str, eventId: str):
        instance = get_object_or_404(Vitals, id=vitalsId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
