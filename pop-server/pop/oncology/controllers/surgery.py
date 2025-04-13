import pghistory

from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
from pop.core.schemas import ModifiedResourceSchema, Paginated, HistoryEvent
from pop.oncology.models import Surgery, TherapyLine

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import SurgerySchema, SurgeryCreateSchema, SurgeryFilters

@api_controller(
    'surgeries', 
    auth=[JWTAuth()], 
    tags=['Surgeries'],  
)
class SurgeryController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[SurgerySchema],
        },
        permissions=[perms.CanViewCases],
        operation_id='getSurgeries',
    )
    @paginate()
    def get_all_surgeries_matching_the_query(self, query: Query[SurgeryFilters]): # type: ignore
        queryset = Surgery.objects.all().order_by('-date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        permissions=[perms.CanManageCases],
        operation_id='createSurgery',
    )
    def create_surgery(self, payload: SurgeryCreateSchema): # type: ignore
        return payload.model_dump_django().assign_therapy_line()

    @route.get(
        path='/{surgeryId}', 
        response={
            200: SurgerySchema,
            404: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getSurgeryById',
    )
    def get_surgery_by_id(self, surgeryId: str):
        return get_object_or_404(Surgery, id=surgeryId)

    @route.put(
        path='/{surgeryId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateSurgeryById',
    )
    def update_surgery(self, surgeryId: str, payload: SurgeryCreateSchema): # type: ignore
        instance = get_object_or_404(Surgery, id=surgeryId)
        return payload.model_dump_django(instance=instance).assign_therapy_line()

    @route.delete(
        path='/{surgeryId}', 
        response={
            204: None, 
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteSurgeryById',
    )
    def delete_surgery(self, surgeryId: str):
        instance = get_object_or_404(Surgery, id=surgeryId)
        case = instance.case
        instance.delete()
        TherapyLine.assign_therapy_lines(case)
        return 204, None
        
    @route.get(
        path='/{surgeryId}/history/events', 
        response={
            200: Paginated[HistoryEvent],
            404: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllSurgeryHistoryEvents',
    )
    @paginate()
    def get_all_surgery_history_events(self, surgeryId: str):
        instance = get_object_or_404(Surgery, id=surgeryId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path='/{surgeryId}/history/events/{eventId}', 
        response={
            200: HistoryEvent,
            404: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getSurgeryHistoryEventById',
    )
    def get_surgery_history_event_by_id(self, surgeryId: str, eventId: str):
        instance = get_object_or_404(Surgery, id=surgeryId)
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)

    @route.put(
        path='/{surgeryId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertSurgeryToHistoryEvent',
    )
    def revert_surgery_to_history_event(self, surgeryId: str, eventId: str):
        instance = get_object_or_404(Surgery, id=surgeryId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()