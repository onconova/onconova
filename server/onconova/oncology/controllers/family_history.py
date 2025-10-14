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
    "family-histories",
    auth=[XSessionTokenAuth()],
    tags=["Family Histories"],
)
class FamilyHistoryController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[scm.FamilyHistory],
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getFamilyHistories",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_family_member_histories_matching_the_query(self, query: Query[scm.FamilyHistoryFilters]):  # type: ignore
        queryset = orm.FamilyHistory.objects.all().order_by("-date")
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createFamilyHistory",
    )
    def create_family_history(self, payload: scm.FamilyHistoryCreate): 
        return 201, payload.model_dump_django()

    @route.get(
        path="/{familyHistoryId}",
        response={200: scm.FamilyHistory, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getFamilyHistoryById",
    )
    @anonymize()
    def get_family_history_by_id(self, familyHistoryId: str):
        return get_object_or_404(orm.FamilyHistory, id=familyHistoryId)

    @route.delete(
        path="/{familyHistoryId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteFamilyHistoryById",
    )
    def delete_family_history(self, familyHistoryId: str):
        get_object_or_404(orm.FamilyHistory, id=familyHistoryId).delete()
        return 204, None

    @route.put(
        path="/{familyHistoryId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateFamilyHistory",
    )
    def update_family_history(self, familyHistoryId: str, payload: scm.FamilyHistoryCreate):
        instance = get_object_or_404(orm.FamilyHistory, id=familyHistoryId)
        return payload.model_dump_django(instance=instance)

    @route.get(
        path="/{familyHistoryId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(scm.FamilyHistoryCreate)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllFamilyHistoryHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_family_history_history_events(self, familyHistoryId: str):
        instance = get_object_or_404(orm.FamilyHistory, id=familyHistoryId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{familyHistoryId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.FamilyHistoryCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getFamilyHistoryHistoryEventById",
    )
    def get_family_history_history_event_by_id(
        self, familyHistoryId: str, eventId: str
    ):
        instance = get_object_or_404(orm.FamilyHistory, id=familyHistoryId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{familyHistoryId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertFamilyHistoryToHistoryEvent",
    )
    def revert_family_history_to_history_event(
        self, familyHistoryId: str, eventId: str
    ):
        instance = get_object_or_404(orm.FamilyHistory, id=familyHistoryId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
