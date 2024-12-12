from enum import Enum

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ResourceIdSchema, Paginated
from pop.oncology.models import Staging

from django.shortcuts import get_object_or_404
from typing import List, Union

from pop.oncology.schemas import (
     TNMStagingSchema, TNMStagingCreateSchema,
     FIGOStagingSchema, FIGOStagingCreateSchema,
     BinetStagingSchema, BinetStagingCreateSchema,
     RaiStagingSchema, RaiStagingCreateSchema,
     BreslowDepthSchema, BreslowDepthCreateSchema,
     ClarkStagingSchema, ClarkStagingCreateSchema,
     ISSStagingSchema, ISSStagingCreateSchema,
     RISSStagingSchema, RISSStagingCreateSchema, 
     GleasonGradeSchema, GleasonGradeCreateSchema,
     INSSStageSchema, INSSStageCreateSchema, 
     INRGSSStageSchema, INRGSSStageCreateSchema,
     WilmsStageSchema, WilmsStageCreateSchema,
     RhabdomyosarcomaClinicalGroupSchema, RhabdomyosarcomaClinicalGroupCreateSchema,
     LymphomaStagingSchema, LymphomaStagingCreateSchema,
)

STAGING_SCHEMAS = (
    TNMStagingSchema, 
    FIGOStagingSchema,
    BinetStagingSchema, 
    RaiStagingSchema, 
    BreslowDepthSchema, 
    ClarkStagingSchema, 
    ISSStagingSchema, 
    RISSStagingSchema,  
    GleasonGradeSchema, 
    INSSStageSchema,  
    INRGSSStageSchema, 
    WilmsStageSchema, 
    RhabdomyosarcomaClinicalGroupSchema, 
    LymphomaStagingSchema,
)

CREATE_STAGING_SCHEMAS = (
    TNMStagingCreateSchema, 
    FIGOStagingCreateSchema,
    BinetStagingCreateSchema,
    RaiStagingCreateSchema,
    BreslowDepthCreateSchema,
    ClarkStagingCreateSchema,
    ISSStagingCreateSchema,
    RISSStagingCreateSchema, 
    GleasonGradeCreateSchema,
    INSSStageCreateSchema, 
    INRGSSStageCreateSchema,
    WilmsStageCreateSchema,
    RhabdomyosarcomaClinicalGroupCreateSchema,
    LymphomaStagingCreateSchema,
)

AnyOfResponseSchemas = Union[STAGING_SCHEMAS]

AnyOfPayloadSchemas = Union[CREATE_STAGING_SCHEMAS]

class QueryParameters(Schema):
    case__id: str = Field(None, alias='caseId')

def cast_to_model_schema(model_instance, schemas, payload=None):
    return next((
        schema.model_validate(payload or model_instance)
            for schema in schemas 
                if isinstance(model_instance, schema.Meta.model) 
    ))
    
@api_controller(
    'stagings/', 
    auth=[JWTAuth()], 
    tags=['Stagings'],  
)
class StagingController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: Paginated[AnyOfResponseSchemas],
        },
        exclude_none=True,
        operation_id='getStagings',
    )
    @paginate()
    def get_all_stagings_matching_the_query(self, query: Query[QueryParameters]):
        queryset = Staging.objects.all().order_by('-date')
        for (lookup, value) in query:
            if value is not None:
                queryset = queryset.filter(**{lookup: value})
        return [cast_to_model_schema(staging.get_domain_staging(), STAGING_SCHEMAS) for staging in queryset]


    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema,
        },
        operation_id='createStaging',
    )
    def create_staging(self, payload: AnyOfPayloadSchemas): # type: ignore
        instance = payload.model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)

    @route.get(
        path='/{stagingId}', 
        response={
            200: AnyOfResponseSchemas, 
            404: None
        },
        exclude_none=True,
        operation_id='getStagingById',
        )
    def get_staging_by_id(self, stagingId: str): 
        instance = get_object_or_404(Staging, id=stagingId)
        return 200, cast_to_model_schema(instance.get_domain_staging(), STAGING_SCHEMAS)


    @route.put(
        path='/{stagingId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateStagingById',
    )
    def update_staging(self, stagingId: str, payload: AnyOfPayloadSchemas): # type: ignore
        instance = get_object_or_404(Staging, id=stagingId)
        instance = cast_to_model_schema(instance.get_domain_staging(), CREATE_STAGING_SCHEMAS, payload)\
                    .model_dump_django(instance=instance.get_domain_staging(), user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{stagingId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteStagingById',
    )
    def delete_staging(self, stagingId: str):
        instance = get_object_or_404(Staging, id=stagingId)
        instance.delete()
        return 204, None
    

