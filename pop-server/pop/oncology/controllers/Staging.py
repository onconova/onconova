from enum import Enum

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from django.shortcuts import get_object_or_404
from typing import List, Union
from typing_extensions import TypeAliasType

from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import Staging, StagingDomain
from pop.oncology.schemas import (
    StagingFilters,
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

RESPONSE_SCHEMAS = (
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

PAYLOAD_SCHEMAS = (
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

AnyResponseSchemas = TypeAliasType('AnyStaging',Union[RESPONSE_SCHEMAS]) # type: ignore# type: ignore
AnyPayloadSchemas = Union[PAYLOAD_SCHEMAS]

def cast_to_model_schema(model_instance, schemas, payload=None):
    return next((
        schema.model_validate(payload or model_instance)
            for schema in schemas 
                if isinstance(model_instance, schema.Meta.model) 
    ))
    
@api_controller(
    'stagings', 
    auth=[JWTAuth()], 
    tags=['Stagings'],  
)
class StagingController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[AnyResponseSchemas],
        },
        exclude_none=True,
        operation_id='getStagings',
    )
    @paginate()
    def get_all_stagings_matching_the_query(self, query: Query[StagingFilters]): # type: ignore
        queryset = Staging.objects.all().order_by('-date')
        return [cast_to_model_schema(staging.get_domain_staging(), RESPONSE_SCHEMAS) for staging in query.filter(queryset)]


    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
        },
        operation_id='createStaging',
    )
    def create_staging(self, payload: AnyPayloadSchemas): # type: ignore
        return payload.model_dump_django(user=self.context.request.user)

    @route.get(
        path='/{stagingId}', 
        response={
            200: AnyResponseSchemas, 
            404: None
        },
        exclude_none=True,
        operation_id='getStagingById',
        )
    def get_staging_by_id(self, stagingId: str): 
        instance = get_object_or_404(Staging, id=stagingId)
        return cast_to_model_schema(instance.get_domain_staging(), RESPONSE_SCHEMAS)


    @route.put(
        path='/{stagingId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateStagingById',
    )
    def update_staging(self, stagingId: str, payload: AnyPayloadSchemas): # type: ignore
        instance = get_object_or_404(Staging, id=stagingId)
        return cast_to_model_schema(instance.get_domain_staging(), PAYLOAD_SCHEMAS, payload)\
                    .model_dump_django(instance=instance.get_domain_staging(), user=self.context.request.user)

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
    

