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
    "neoplastic-entities",
    auth=[XSessionTokenAuth()],
    tags=["Neoplastic Entities"],
)
class NeoplasticEntityController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[scm.NeoplasticEntity],
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getNeoplasticEntities",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_neoplastic_entities_matching_the_query(self, query: Query[scm.NeoplasticEntityFilters]):  # type: ignore
        queryset = orm.NeoplasticEntity.objects.all().order_by("-assertion_date")
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createNeoplasticEntity",
    )
    def create_neoplastic_entity(self, payload: scm.NeoplasticEntityCreate):  # type: ignore
        return 201, payload.model_dump_django()

    @route.get(
        path="/{entityId}",
        response={200: scm.NeoplasticEntity, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getNeoplasticEntityById",
    )
    @anonymize()
    def get_neoplastic_entity_by_id(self, entityId: str):
        return get_object_or_404(orm.NeoplasticEntity, id=entityId)

    @route.put(
        path="/{entityId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateNeoplasticEntityById",
    )
    def update_neoplastic_entity(self, entityId: str, payload: scm.NeoplasticEntityCreate):  # type: ignore
        instance = get_object_or_404(orm.NeoplasticEntity, id=entityId)
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{entityId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteNeoplasticEntityById",
    )
    def delete_neoplastic_entity(self, entityId: str):
        get_object_or_404(orm.NeoplasticEntity, id=entityId).delete()
        return 204, None

    @route.get(
        path="/{entityId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(scm.NeoplasticEntityCreate)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllNeoplasticEntityHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_neoplastic_entity_history_events(self, entityId: str):
        instance = get_object_or_404(orm.NeoplasticEntity, id=entityId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{entityId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.NeoplasticEntityCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getNeoplasticEntityHistoryEventById",
    )
    def get_neoplastic_entity_history_event_by_id(self, entityId: str, eventId: str):
        instance = get_object_or_404(orm.NeoplasticEntity, id=entityId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{entityId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertNeoplasticEntityToHistoryEvent",
    )
    def revert_neoplastic_entity_to_history_event(self, entityId: str, eventId: str):
        instance = get_object_or_404(orm.NeoplasticEntity, id=entityId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()