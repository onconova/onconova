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
from onconova.oncology import (
    models as orm,
    schemas as scm,
)

@api_controller(
    "surgeries",
    auth=[XSessionTokenAuth()],
    tags=["Surgeries"],
)
class SurgeryController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[scm.Surgery],
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getSurgeries",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_surgeries_matching_the_query(self, query: Query[scm.SurgeryFilters]):  # type: ignore
        queryset = orm.Surgery.objects.all().order_by("-date")
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createSurgery",
    )
    def create_surgery(self, payload: scm.SurgeryCreate):  # type: ignore
        instance: Surgery = payload.model_dump_django()  # type: ignore
        return 201, instance.assign_therapy_line()

    @route.get(
        path="/{surgeryId}",
        response={200: scm.Surgery, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getSurgeryById",
    )
    @anonymize()
    def get_surgery_by_id(self, surgeryId: str):
        return get_object_or_404(orm.Surgery, id=surgeryId)

    @route.put(
        path="/{surgeryId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateSurgeryById",
    )
    def update_surgery(self, surgeryId: str, payload: scm.SurgeryCreate):  
        instance = get_object_or_404(orm.Surgery, id=surgeryId)
        return payload.model_dump_django(instance=instance).assign_therapy_line()

    @route.delete(
        path="/{surgeryId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteSurgeryById",
    )
    def delete_surgery(self, surgeryId: str):
        instance = get_object_or_404(orm.Surgery, id=surgeryId)
        case = instance.case
        instance.delete()
        orm.TherapyLine.assign_therapy_lines(case)
        return 204, None

    @route.get(
        path="/{surgeryId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(scm.SurgeryCreate)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllSurgeryHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_surgery_history_events(self, surgeryId: str):
        instance = get_object_or_404(orm.Surgery, id=surgeryId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{surgeryId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.SurgeryCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getSurgeryHistoryEventById",
    )
    def get_surgery_history_event_by_id(self, surgeryId: str, eventId: str):
        instance = get_object_or_404(orm.Surgery, id=surgeryId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{surgeryId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertSurgeryToHistoryEvent",
    )
    def revert_surgery_to_history_event(self, surgeryId: str, eventId: str):
        instance = get_object_or_404(orm.Surgery, id=surgeryId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
