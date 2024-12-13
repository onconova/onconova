from enum import Enum

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ResourceIdSchema, Paginated
from pop.oncology.models import TumorMarker
from pop.oncology.models.TumorMarker import AnalyteDetails, ANALYTES_DATA

from django.shortcuts import get_object_or_404
from typing import List

from pop.oncology.schemas import TumorMarkerSchema, TumorMarkerCreateSchema

class QueryParameters(Schema):
    case__id: str = Field(None, alias='caseId')

@api_controller(
    'tumor-markers/', 
    auth=[JWTAuth()], 
    tags=['Tumor Markers'],  
)
class TumorMarkerController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: Paginated[TumorMarkerSchema],
        },
        operation_id='getTumorMarkers',
    )
    @paginate()
    def get_all_tumor_markers_matching_the_query(self, query: Query[QueryParameters]):
        queryset = TumorMarker.objects.all().order_by('-date')
        for (lookup, value) in query:
            if value is not None:
                queryset = queryset.filter(**{lookup: value})
        return [TumorMarkerSchema.model_validate(instance) for instance in queryset]

    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema
        },
        operation_id='createTumorMarker',
    )
    def create_tumor_marker(self, payload: TumorMarkerCreateSchema): # type: ignore
        instance = TumorMarkerCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)

    @route.get(
        path='/{tumorMarkerId}', 
        response={
            200: TumorMarkerSchema,
            404: None,
        },
        operation_id='getTumorMarkerById',
    )
    def get_tumor_marker_by_id(self, tumorMarkerId: str):
        instance = get_object_or_404(TumorMarker, id=tumorMarkerId)
        return 200, TumorMarkerSchema.model_validate(instance)

    @route.put(
        path='/{tumorMarkerId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateTumorMarkerById',
    )
    def update_neoplastic_entity(self, tumorMarkerId: str, payload: TumorMarkerCreateSchema): # type: ignore
        instance = get_object_or_404(TumorMarker, id=tumorMarkerId)
        instance = TumorMarkerCreateSchema\
                    .model_validate(payload.model_dump(exclude_unset=True))\
                    .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{tumorMarkerId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteTumorMarkerById',
    )
    def delete_tumor_marker(self, tumorMarkerId: str):
        instance = get_object_or_404(TumorMarker, id=tumorMarkerId)
        instance.delete()
        return 204, None
    
    
    @route.get(
        path='analytes/{analyteCode}/details', 
        response={
            200: AnalyteDetails,
            404: None,
        },
        operation_id='getTumorMarkerAnalyteDetails',
    )
    def get_tumor_marker_analyte_details(self, analyteCode: str):
        instance = ANALYTES_DATA.get(analyteCode)
        if instance is None:
            return 404, None
        return 200, instance
