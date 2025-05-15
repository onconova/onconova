import pghistory
from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
from pop.core.security import XSessionTokenAuth
from pop.core.schemas import ModifiedResourceSchema, Paginated, HistoryEvent
from pop.oncology.models import Lifestyle

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import LifestyleSchema, LifestyleCreateSchema, LifestyleFilters


@api_controller(
    'lifestyles', 
    auth=[XSessionTokenAuth()], 
    tags=['Lifestyles'],  
)
class LifestyleController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[LifestyleSchema],
        },
        permissions=[perms.CanViewCases],
        operation_id='getLifestyles',
    )
    @paginate()
    def get_all_lifestyles_matching_the_query(self, query: Query[LifestyleFilters]): # type: ignore
        queryset = Lifestyle.objects.all().order_by('-date')
        return query.filter(queryset)


    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='createLifestyle',
    )
    def create_lifestyle(self, payload: LifestyleCreateSchema): # type: ignore
        return 201, payload.model_dump_django()
        

    @route.get(
        path='/{lifestyleId}', 
        response={
            200: LifestyleSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getLifestyleById',
    )
    def get_lifestyle_by_id(self, lifestyleId: str):
        return get_object_or_404(Lifestyle, id=lifestyleId)
        
        
    @route.put(
        path='/{lifestyleId}', 
       response={
            200: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateLifestyleById',
    )
    def update_lifestyle(self, lifestyleId: str, payload: LifestyleCreateSchema): # type: ignore
        instance = get_object_or_404(Lifestyle, id=lifestyleId)
        return payload.model_dump_django(instance=instance)
        
    @route.delete(
        path='/{lifestyleId}', 
        response={
            204: None, 
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteLifestyleById',
    )
    def delete_lifestyle(self, lifestyleId: str):
        get_object_or_404(Lifestyle, id=lifestyleId).delete()
        return 204, None
    
    @route.get(
        path='/{lifestyleId}/history/events', 
        response={
            200: Paginated[HistoryEvent.bind_schema(LifestyleCreateSchema)],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllLifestyleHistoryEvents',
    )
    @paginate()
    def get_all_lifestyle_history_events(self, lifestyleId: str):
        instance = get_object_or_404(Lifestyle, id=lifestyleId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path='/{lifestyleId}/history/events/{eventId}', 
        response={
            200: HistoryEvent.bind_schema(LifestyleCreateSchema),
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getLifestyleHistoryEventById',
    )
    def get_lifestyle_history_event_by_id(self, lifestyleId: str, eventId: str):
        instance = get_object_or_404(Lifestyle, id=lifestyleId)
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)

    @route.put(
        path='/{lifestyleId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertLifestyleToHistoryEvent',
    )
    def revert_lifestyle_to_history_event(self, lifestyleId: str, eventId: str):
        instance = get_object_or_404(Lifestyle, id=lifestyleId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()