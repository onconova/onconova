from typing import List

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ResourceIdSchema, Paginated
from pop.oncology.models import AdverseEvent, AdverseEventSuspectedCause, AdverseEventMitigation

from django.shortcuts import get_object_or_404
from django.db import transaction

from pop.oncology.schemas import (
    AdverseEventSchema, AdverseEventCreateSchema,
    AdverseEventSuspectedCauseSchema, AdverseEventSuspectedCauseCreateSchema,
    AdverseEventMitigationSchema, AdverseEventMitigationCreateSchema,    
)


class QueryParameters(Schema):
    case__id: str = Field(None, alias='caseId')

@api_controller(
    'adverse-events/', 
    auth=[JWTAuth()], 
    tags=['Adverse Events'],  
)
class AdverseEventController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: Paginated[AdverseEventSchema],
        },
        operation_id='getAdverseEvents',
    )
    @paginate()
    def get_all_adverse_events_matching_the_query(self, query: Query[QueryParameters]):
        queryset = AdverseEvent.objects.all().order_by('-date')
        for (lookup, value) in query:
            if value is not None:
                queryset = queryset.filter(**{lookup: value})
        return [AdverseEventSchema.model_validate(instance) for instance in queryset]

    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema
        },
        operation_id='createAdverseEvent',
    )
    def create_adverse_event(self, payload: AdverseEventCreateSchema): # type: ignore
        instance = AdverseEventCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)
    
    @route.get(
        path='/{adverseEventId}', 
        response={
            200: AdverseEventSchema,
            404: None,
        },
        operation_id='getAdverseEventById',
    )
    def get_adverse_event_by_id(self, adverseEventId: str):
        instance = get_object_or_404(AdverseEvent, id=adverseEventId)
        return 200, AdverseEventSchema.model_validate(instance)

    @route.put(
        path='/', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateAdverseEvent',
    )
    def update_adverse_event(self, payload: AdverseEventCreateSchema): # type: ignore
        with transaction.atomic():
            instance = get_object_or_404(AdverseEvent, id=payload.id)
            instance = AdverseEventCreateSchema\
                        .model_validate(payload.model_dump(exclude_unset=True))\
                        .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{adverseEventId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteAdverseEventById',
    )
    def delete_adverse_event(self, adverseEventId: str):
        instance = get_object_or_404(AdverseEvent, id=adverseEventId)
        instance.delete()
        return 204, None
    
    
    @route.put(
        path='/{adverseEventId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateAdverseEvent',
    )
    def update_adverse_event(self, adverseEventId: str, payload: AdverseEventCreateSchema): # type: ignore
        with transaction.atomic():
            instance = get_object_or_404(AdverseEvent, id=adverseEventId)
            instance = AdverseEventCreateSchema\
                        .model_validate(payload.model_dump(exclude_unset=True))\
                        .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None
    


    @route.get(
        path='/{adverseEventId}/suspected-causes/', 
        response={
            200: List[AdverseEventSuspectedCauseSchema],
            404: None,
        },
        operation_id='getAdverseEventSuspectedCauses',
    )
    def get_adverse_event_suspected_causes_matching_the_query(self, adverseEventId: str): # type: ignore
        queryset = get_object_or_404(AdverseEvent, id=adverseEventId).suspected_causes.all()
        return 200, [AdverseEventSuspectedCauseSchema.model_validate(entry) for entry in queryset]


    @route.get(
        path='/{adverseEventId}/suspected-causes/{causeId}', 
        response={
            200: AdverseEventSuspectedCauseSchema,
            404: None,
        },
        operation_id='getAdverseEventSuspectedCauseById',
    )
    def get_adverse_event_suspected_cause_by_id(self, adverseEventId: str, causeId: str): # type: ignore
        instance = get_object_or_404(AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId)
        return 200, AdverseEventSuspectedCauseSchema.model_validate(instance)

    @route.post(
        path='/{adverseEventId}/suspected-causes/', 
        response={
            201: ResourceIdSchema,
            404: None,
        },
        operation_id='createAdverseEventSuspectedCause',
    )
    def create_adverse_event_suspected_cause(self, adverseEventId: str, payload: AdverseEventSuspectedCauseCreateSchema): # type: ignore
        instance = AdverseEventSuspectedCause(adverse_event=get_object_or_404(AdverseEvent, id=adverseEventId))
        instance = AdverseEventSuspectedCauseCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(instance=instance, user=self.context.request.user, create=True)
        return 201, ResourceIdSchema(id=instance.id)


    @route.put(
        path='/{adverseEventId}/suspected-causes/{causeId}', 
        response={
            204: ResourceIdSchema,
            404: None,
        },
        operation_id='updateAdverseEventSuspectedCause',
    )
    def update_adverse_event_suspected_cause(self, adverseEventId: str, causeId: str, payload: AdverseEventSuspectedCauseCreateSchema): # type: ignore
        instance = get_object_or_404(AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId)
        instance = AdverseEventSuspectedCauseCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, ResourceIdSchema(id=instance.id)
    

    @route.delete(
        path='/{adverseEventId}/suspected-causes/{causeId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteAdverseEventSuspectedCause',
    )
    def delete_adverse_event_suspected_cause(self, adverseEventId: str, causeId: str):
        instance = get_object_or_404(AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId)
        instance.delete()
        return 204, None
    
    
    
    
    @route.get(
        path='/{adverseEventId}/mitigations/', 
        response={
            200: List[AdverseEventMitigationSchema],
            404: None,
        },
        operation_id='getAdverseEventMitigations',
    )
    def get_adverse_event_mitigations_matching_the_query(self, adverseEventId: str): # type: ignore
        queryset = get_object_or_404(AdverseEvent, id=adverseEventId).mitigations.all()
        return 200, [AdverseEventMitigationSchema.model_validate(entry) for entry in queryset]


    @route.get(
        path='/{adverseEventId}/mitigations/{mitigationId}', 
        response={
            200: AdverseEventMitigationSchema,
            404: None,
        },
        operation_id='getAdverseEventMitigationById',
    )
    def get_adverse_event_mitigation_by_id(self, adverseEventId: str, mitigationId: str): # type: ignore
        instance = get_object_or_404(AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId)
        return 200, AdverseEventMitigationSchema.model_validate(instance)

    @route.post(
        path='/{adverseEventId}/mitigations/', 
        response={
            201: ResourceIdSchema,
            404: None,
        },
        operation_id='createAdverseEventMitigation',
    )
    def create_adverse_event_mitigation(self, adverseEventId: str, payload: AdverseEventMitigationCreateSchema): # type: ignore
        instance = AdverseEventMitigation(adverse_event=get_object_or_404(AdverseEvent, id=adverseEventId))
        instance = AdverseEventMitigationCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(instance=instance, user=self.context.request.user, create=True)
        return 201, ResourceIdSchema(id=instance.id)


    @route.put(
        path='/{adverseEventId}/mitigations/{mitigationId}', 
        response={
            204: ResourceIdSchema,
            404: None,
        },
        operation_id='updateAdverseEventMitigation',
    )
    def update_adverse_event_mitigation(self, adverseEventId: str, mitigationId: str, payload: AdverseEventMitigationCreateSchema): # type: ignore
        instance = get_object_or_404(AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId)
        instance = AdverseEventMitigationCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, ResourceIdSchema(id=instance.id)
    

    @route.delete(
        path='/{adverseEventId}/mitigations/{mitigationId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteAdverseEventMitigation',
    )
    def delete_adverse_event_mitigation(self, adverseEventId: str, mitigationId: str):
        instance = get_object_or_404(AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId)
        instance.delete()
        return 204, None
    