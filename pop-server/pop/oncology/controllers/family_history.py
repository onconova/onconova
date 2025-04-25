import pghistory

from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
from pop.core.schemas import ModifiedResourceSchema, Paginated, HistoryEvent
from pop.oncology.models import FamilyHistory

from django.shortcuts import get_object_or_404
from pop.oncology.schemas import FamilyHistorySchema, FamilyHistoryCreateSchema, FamilyHistoryFilters

@api_controller(
    'family-histories', 
    auth=[JWTAuth()], 
    tags=['Family Histories'],  
)
class FamilyHistoryController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[FamilyHistorySchema],
        },
        permissions=[perms.CanViewCases],
        operation_id='getFamilyHistories',
    )
    @paginate()
    def get_all_family_member_histories_matching_the_query(self, query: Query[FamilyHistoryFilters]): # type: ignore
        queryset = FamilyHistory.objects.all().order_by('-date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='createFamilyHistory',
    )
    def create_family_history(self, payload: FamilyHistoryCreateSchema): # type: ignore
        return 201, payload.model_dump_django()
        

    @route.get(
        path='/{familyHistoryId}', 
        response={
            200: FamilyHistorySchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getFamilyHistoryById',
    )
    def get_family_history_by_id(self, familyHistoryId: str):
        return get_object_or_404(FamilyHistory, id=familyHistoryId)
        

    @route.delete(
        path='/{familyHistoryId}', 
        response={
            204: None, 
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteFamilyHistoryById',
    )
    def delete_family_history(self, familyHistoryId: str):
        get_object_or_404(FamilyHistory, id=familyHistoryId).delete()
        return 204, None
    
    
    @route.put(
        path='/{familyHistoryId}', 
       response={
            200: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateFamilyHistory',
    )
    def update_family_history(self, familyHistoryId: str, payload: FamilyHistoryCreateSchema): # type: ignore
        instance = get_object_or_404(FamilyHistory, id=familyHistoryId)
        return payload.model_dump_django(instance=instance)

    @route.get(
        path='/{familyHistoryId}/history/events', 
        response={
            200: Paginated[HistoryEvent.bind_schema(FamilyHistoryCreateSchema)],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllFamilyHistoryHistoryEvents',
    )
    @paginate()
    def get_all_family_history_history_events(self, familyHistoryId: str):
        instance = get_object_or_404(FamilyHistory, id=familyHistoryId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path='/{familyHistoryId}/history/events/{eventId}', 
        response={
            200: HistoryEvent.bind_schema(FamilyHistoryCreateSchema),
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getFamilyHistoryHistoryEventById',
    )
    def get_family_history_history_event_by_id(self, familyHistoryId: str, eventId: str):
        instance = get_object_or_404(FamilyHistory, id=familyHistoryId)
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)

    @route.put(
        path='/{familyHistoryId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertFamilyHistoryToHistoryEvent',
    )
    def revert_family_history_to_history_event(self, familyHistoryId: str, eventId: str):
        instance = get_object_or_404(FamilyHistory, id=familyHistoryId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()