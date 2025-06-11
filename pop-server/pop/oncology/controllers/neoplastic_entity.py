from enum import Enum
import pghistory 

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth
from pop.core.anonymization import anonymize
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema, Paginated
from pop.core.history.schemas import HistoryEvent
from pop.oncology.models import NeoplasticEntity

from django.shortcuts import get_object_or_404
from typing import List

from pop.oncology.schemas import NeoplasticEntitySchema, NeoplasticEntityCreateSchema, NeoplasticEntityFilters


@api_controller(
    'neoplastic-entities', 
    auth=[XSessionTokenAuth()], 
    tags=['Neoplastic Entities'],  
)
class NeoplasticEntityController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[NeoplasticEntitySchema],
        },
        permissions=[perms.CanViewCases],
        operation_id='getNeoplasticEntities',
    )
    @paginate()
    @anonymize()
    def get_all_neoplastic_entities_matching_the_query(self, query: Query[NeoplasticEntityFilters], anonymized: bool = True): # type: ignore
        queryset = NeoplasticEntity.objects.all().order_by('-assertion_date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='createNeoplasticEntity',
    )
    def create_neoplastic_entity(self, payload: NeoplasticEntityCreateSchema): # type: ignore
        return 201, payload.model_dump_django()
        
    @route.get(
        path='/{entityId}', 
        response={
            200: NeoplasticEntitySchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getNeoplasticEntityById',
    )
    @anonymize()
    def get_neoplastic_entity_by_id(self, entityId: str, anonymized: bool = True):
        return get_object_or_404(NeoplasticEntity, id=entityId)
        
    @route.put(
        path='/{entityId}', 
       response={
            200: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateNeoplasticEntityById',
    )
    def update_neoplastic_entity(self, entityId: str, payload: NeoplasticEntityCreateSchema): # type: ignore
        instance = get_object_or_404(NeoplasticEntity, id=entityId)
        return payload.model_dump_django(instance=instance)
        
    @route.delete(
        path='/{entityId}', 
        response={
            204: None, 
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteNeoplasticEntityById',
    )
    def delete_neoplastic_entity(self, entityId: str):
        get_object_or_404(NeoplasticEntity, id=entityId).delete()
        return 204, None
    
    @route.get(
        path='/{entityId}/history/events', 
        response={
            200: Paginated[HistoryEvent.bind_schema(NeoplasticEntityCreateSchema)],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllNeoplasticEntityHistoryEvents',
    )
    @paginate()
    def get_all_neoplastic_entity_history_events(self, entityId: str):
        instance = get_object_or_404(NeoplasticEntity, id=entityId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path='/{entityId}/history/events/{eventId}', 
        response={
            200: HistoryEvent.bind_schema(NeoplasticEntityCreateSchema),
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getNeoplasticEntityHistoryEventById',
    )
    def get_neoplastic_entity_history_event_by_id(self, entityId: str, eventId: str):
        instance = get_object_or_404(NeoplasticEntity, id=entityId)
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)

    @route.put(
        path='/{entityId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertNeoplasticEntityToHistoryEvent',
    )
    def revert_neoplastic_entity_to_history_event(self, entityId: str, eventId: str):
        instance = get_object_or_404(NeoplasticEntity, id=entityId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()