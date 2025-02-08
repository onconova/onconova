from enum import Enum

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ModifiedResourceSchema, Paginated
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
        operation_id='getTumorMarkers',
    )
    @paginate()
    def get_all_tumor_markers_matching_the_query(self, query: Query[TumorMarkerFilters]): # type: ignore
        queryset = TumorMarker.objects.all().order_by('-date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createTumorMarker',
    )
    def create_tumor_marker(self, payload: TumorMarkerCreateSchema): # type: ignore
        return payload.model_dump_django(user=self.context.request.user)
        

    @route.get(
        path='/{tumorMarkerId}', 
        response={
            200: TumorMarkerSchema,
            404: None,
        },
        operation_id='getTumorMarkerById',
    )
    def get_tumor_marker_by_id(self, tumorMarkerId: str):
        return get_object_or_404(TumorMarker, id=tumorMarkerId)
        
        
    @route.put(
        path='/{tumorMarkerId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateTumorMarkerById',
    )
    def update_neoplastic_entity(self, tumorMarkerId: str, payload: TumorMarkerCreateSchema): # type: ignore
        instance = get_object_or_404(TumorMarker, id=tumorMarkerId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
        
        
    @route.delete(
        path='/{tumorMarkerId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteTumorMarkerById',
    )
    def delete_tumor_marker(self, tumorMarkerId: str):
        get_object_or_404(TumorMarker, id=tumorMarkerId).delete()
        return 204, None

    @route.get(
        path='analytes/{analyteCode}/details', 
        response={
            200: AnalyteDetails,
            404: None,
        },
        operation_id='getTumorMarkerAnalyteDetailsByCode',
    )
    def get_tumor_marker_analyte_details_by_code(self, analyteCode: str):
        instance = ANALYTES_DATA.get(analyteCode)
        if instance is None:
            return 404, None
        return 200, instance
