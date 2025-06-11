import pghistory
from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route
from typing import List

from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth
from pop.core.anonymization import anonymize
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema, Paginated
from pop.core.history.schemas import HistoryEvent
from pop.oncology.models import TherapyLine, PatientCase

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import TherapyLineSchema, TherapyLineCreateSchema, TherapyLineFilters

@api_controller(
    'therapy-lines', 
    auth=[XSessionTokenAuth()], 
    tags=['Therapy Lines'],  
)
class TherapyLineController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[TherapyLineSchema],
        },
        permissions=[perms.CanViewCases],
        operation_id='getTherapyLines',
    )
    @paginate()
    @anonymize()
    def get_all_therapy_lines_matching_the_query(self, query: Query[TherapyLineFilters], anonymized: bool = True): # type: ignore
        queryset = TherapyLine.objects.all().order_by('-period')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='createTherapyLine',
    )
    def create_therapy_line(self, payload: TherapyLineCreateSchema): # type: ignore
        return 201, payload.model_dump_django()

    @route.get(
        path='/{therapyLineId}', 
        response={
            200: TherapyLineSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getTherapyLineById',
    )
    @anonymize()
    def get_therapy_line_by_id(self, therapyLineId: str, anonymized: bool = True):
        return get_object_or_404(TherapyLine, id=therapyLineId)


    @route.put(
        path='/{therapyLineId}', 
       response={
            200: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateTherapyLine',
    )
    def update_therapy_line(self, therapyLineId: str, payload: TherapyLineCreateSchema): # type: ignore
        instance = get_object_or_404(TherapyLine, id=therapyLineId)
        return payload.model_dump_django(instance=instance)
        
    @route.delete(
        path='/{therapyLineId}', 
        response={
            204: None, 
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteTherapyLine',
    )
    def delete_therapy_line(self, therapyLineId: str):
        get_object_or_404(TherapyLine, id=therapyLineId).delete()
        return 204, None
    
    @route.get(
        path='/{therapyLineId}/history/events', 
        response={
            200: Paginated[HistoryEvent.bind_schema(TherapyLineCreateSchema)],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllTherapyLineHistoryEvents',
    )
    @paginate()
    def get_all_therapy_line_history_events(self, therapyLineId: str):
        instance = get_object_or_404(TherapyLine, id=therapyLineId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path='/{therapyLineId}/history/events/{eventId}', 
        response={
            200: HistoryEvent.bind_schema(TherapyLineCreateSchema),
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getTherapyLineHistoryEventById',
    )
    def get_therapy_line_history_event_by_id(self, therapyLineId: str, eventId: str):
        instance = get_object_or_404(TherapyLine, id=therapyLineId)
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)

    @route.put(
        path='/{therapyLineId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertTherapyLineToHistoryEvent',
    )
    def revert_therapy_line_to_history_event(self, therapyLineId: str, eventId: str):
        instance = get_object_or_404(TherapyLine, id=therapyLineId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
    
    @route.get(
        path='/{caseId}/re-assignments', 
        response={
            200: List[TherapyLineSchema],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getReassignedPatientCaseTherapyLines',
    )
    def get_reassigned_patient_case_therapy_lines(self, caseId: str):
        return TherapyLine.assign_therapy_lines(get_object_or_404(PatientCase, id=caseId))
