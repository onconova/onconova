import pghistory

from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
from pop.core.schemas import ModifiedResourceSchema, Paginated, HistoryEvent
from pop.oncology.models import TumorMarker
from pop.oncology.models.tumor_marker import AnalyteDetails, ANALYTES_DATA

from django.shortcuts import get_object_or_404
from typing import List,Dict

from pop.oncology.schemas import TumorMarkerSchema, TumorMarkerCreateSchema, TumorMarkerFilters

@api_controller(
    'tumor-markers', 
    auth=[JWTAuth()], 
    tags=['Tumor Markers'],  
)
class TumorMarkerController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[TumorMarkerSchema],
        },
        permissions=[perms.CanViewCases],
        operation_id='getTumorMarkers',
    )
    @paginate()
    def get_all_tumor_markers_matching_the_query(self, query: Query[TumorMarkerFilters]): # type: ignore
        queryset = TumorMarker.objects.all().order_by('-date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='createTumorMarker',
    )
    def create_tumor_marker(self, payload: TumorMarkerCreateSchema): # type: ignore
        return 201, payload.model_dump_django()

    @route.get(
        path='/{tumorMarkerId}', 
        response={
            200: TumorMarkerSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getTumorMarkerById',
    )
    def get_tumor_marker_by_id(self, tumorMarkerId: str):
        return get_object_or_404(TumorMarker, id=tumorMarkerId)
        
    @route.put(
        path='/{tumorMarkerId}', 
       response={
            200: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateTumorMarkerById',
    )
    def update_neoplastic_entity(self, tumorMarkerId: str, payload: TumorMarkerCreateSchema): # type: ignore
        instance = get_object_or_404(TumorMarker, id=tumorMarkerId)
        return payload.model_dump_django(instance=instance)
        
    @route.delete(
        path='/{tumorMarkerId}', 
        response={
            204: None, 
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteTumorMarkerById',
    )
    def delete_tumor_marker(self, tumorMarkerId: str):
        get_object_or_404(TumorMarker, id=tumorMarkerId).delete()
        return 204, None
    
    @route.get(
        path='/{tumorMarkerId}/history/events', 
        response={
            200: Paginated[HistoryEvent],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllTumorMarkerHistoryEvents',
    )
    @paginate()
    def get_all_tumor_marker_history_events(self, tumorMarkerId: str):
        instance = get_object_or_404(TumorMarker, id=tumorMarkerId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path='/{tumorMarkerId}/history/events/{eventId}', 
        response={
            200: HistoryEvent,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getTumorMarkerHistoryEventById',
    )
    def get_tumor_marker_history_event_by_id(self, tumorMarkerId: str, eventId: str):
        instance = get_object_or_404(TumorMarker, id=tumorMarkerId)
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)

    @route.put(
        path='/{tumorMarkerId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertTumorMarkerToHistoryEvent',
    )
    def revert_tumor_marker_to_history_event(self, tumorMarkerId: str, eventId: str):
        instance = get_object_or_404(TumorMarker, id=tumorMarkerId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
    

    @route.get(
        path='analytes/{analyteCode}/details', 
        response={
            200: AnalyteDetails,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getTumorMarkerAnalyteDetailsByCode',
    )
    def get_tumor_marker_analyte_details_by_code(self, analyteCode: str):
        instance = ANALYTES_DATA.get(analyteCode)
        if instance is None:
            return 404, None
        return 200, instance
