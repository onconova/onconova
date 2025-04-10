import pghistory

from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from typing import Union
from typing_extensions import TypeAliasType

from pop.core import permissions as perms
from pop.core.utils import revert_multitable_model
from pop.core.schemas import ModifiedResourceSchema, Paginated, HistoryEvent
from pop.oncology.models import Staging
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
                if (payload and payload.stagingDomain == schema.model_fields['stagingDomain'].default)  or (model_instance and model_instance.staging_domain == schema.model_fields['stagingDomain'].default)
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
        permissions=[perms.CanViewCases],
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
        permissions=[perms.CanManageCases],
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
        permissions=[perms.CanViewCases],
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
        permissions=[perms.CanManageCases],
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
        permissions=[perms.CanManageCases],
        operation_id='deleteStagingById',
    )
    def delete_staging(self, stagingId: str):
        instance = get_object_or_404(Staging, id=stagingId)
        instance.delete()
        return 204, None
    
    @route.get(
        path='/{stagingId}/history/events', 
        response={
            200: Paginated[HistoryEvent],
            404: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllStagingHistoryEvents',
    )
    @paginate()
    def get_all_staging_history_events(self, stagingId: str):
        instance = get_object_or_404(Staging, id=stagingId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path='/{stagingId}/history/events/{eventId}', 
        response={
            200: HistoryEvent,
            404: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getStagingHistoryEventById',
    )
    def get_staging_history_event_by_id(self, stagingId: str, eventId: str):
        instance = get_object_or_404(Staging, id=stagingId)
        event = instance.parent_events.filter(pgh_id=eventId).first()
        if not event and hasattr(instance, 'events'):
            event = instance.events.filter(pgh_id=eventId).first()
        if not event:
            return 404, None
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)

    @route.put(
        path='/{stagingId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertStagingToHistoryEvent',
    )
    def revert_staging_to_history_event(self, stagingId: str, eventId: str):
        instance = get_object_or_404(Staging, id=stagingId)
        instance = instance.get_domain_staging()
        try:
            return 201, revert_multitable_model(instance, eventId)
        except ObjectDoesNotExist:
            return 404, None

