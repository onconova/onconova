from typing import List

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import AdverseEvent, AdverseEventSuspectedCause, AdverseEventMitigation

from django.shortcuts import get_object_or_404
from django.db import transaction

from pop.oncology.schemas import (
    AdverseEventSchema, AdverseEventCreateSchema,
    AdverseEventSuspectedCauseSchema, AdverseEventSuspectedCauseCreateSchema,
    AdverseEventMitigationSchema, AdverseEventMitigationCreateSchema,    
    AdverseEventFilters
)

@api_controller(
    'adverse-events', 
    auth=[JWTAuth()], 
    tags=['Adverse Events'],  
)
class AdverseEventController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[AdverseEventSchema],
        },
        operation_id='getAdverseEvents',
    )
    @paginate()
    def get_all_adverse_events_matching_the_query(self, query: Query[AdverseEventFilters]):  # type: ignore
        queryset = AdverseEvent.objects.all().order_by('-date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createAdverseEvent',
    )
    def create_adverse_event(self, payload: AdverseEventCreateSchema): # type: ignore
        return AdverseEventCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
    
    @route.get(
        path='/{adverseEventId}', 
        response={
            200: AdverseEventSchema,
            404: None,
        },
        operation_id='getAdverseEventById',
    )
    def get_adverse_event_by_id(self, adverseEventId: str):
        return get_object_or_404(AdverseEvent, id=adverseEventId)

    @route.delete(
        path='/{adverseEventId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteAdverseEventById',
    )
    def delete_adverse_event(self, adverseEventId: str):
        get_object_or_404(AdverseEvent, id=adverseEventId).delete()
        return 204, None
    
    
    @route.put(
        path='/{adverseEventId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateAdverseEvent',
    )
    def update_adverse_event(self, adverseEventId: str, payload: AdverseEventCreateSchema): # type: ignore
        instance = get_object_or_404(AdverseEvent, id=adverseEventId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)    


    @route.get(
        path='/{adverseEventId}/suspected-causes', 
        response={
            200: List[AdverseEventSuspectedCauseSchema],
            404: None,
        },
        operation_id='getAdverseEventSuspectedCauses',
    )
    def get_adverse_event_suspected_causes_matching_the_query(self, adverseEventId: str): # type: ignore
        return get_object_or_404(AdverseEvent, id=adverseEventId).suspected_causes.all()
        


    @route.get(
        path='/{adverseEventId}/suspected-causes/{causeId}', 
        response={
            200: AdverseEventSuspectedCauseSchema,
            404: None,
        },
        operation_id='getAdverseEventSuspectedCauseById',
    )
    def get_adverse_event_suspected_cause_by_id(self, adverseEventId: str, causeId: str): # type: ignore
        return get_object_or_404(AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId)

    @route.post(
        path='/{adverseEventId}/suspected-causes', 
        response={
            201: ModifiedResourceSchema,
        },
        operation_id='createAdverseEventSuspectedCause',
    )
    def create_adverse_event_suspected_cause(self, adverseEventId: str, payload: AdverseEventSuspectedCauseCreateSchema): # type: ignore
        instance = AdverseEventSuspectedCause(adverse_event=get_object_or_404(AdverseEvent, id=adverseEventId))
        return payload.model_dump_django(instance=instance, user=self.context.request.user, create=True)

    @route.put(
        path='/{adverseEventId}/suspected-causes/{causeId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateAdverseEventSuspectedCause',
    )
    def update_adverse_event_suspected_cause(self, adverseEventId: str, causeId: str, payload: AdverseEventSuspectedCauseCreateSchema): # type: ignore
        instance = get_object_or_404(AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)


    @route.delete(
        path='/{adverseEventId}/suspected-causes/{causeId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteAdverseEventSuspectedCause',
    )
    def delete_adverse_event_suspected_cause(self, adverseEventId: str, causeId: str):
        get_object_or_404(AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId).delete()
        return 204, None
    
    
    @route.get(
        path='/{adverseEventId}/mitigations', 
        response={
            200: List[AdverseEventMitigationSchema],
            404: None,
        },
        operation_id='getAdverseEventMitigations',
    )
    def get_adverse_event_mitigations_matching_the_query(self, adverseEventId: str): # type: ignore
        return get_object_or_404(AdverseEvent, id=adverseEventId).mitigations.all()
        

    @route.get(
        path='/{adverseEventId}/mitigations/{mitigationId}', 
        response={
            200: AdverseEventMitigationSchema,
            404: None,
        },
        operation_id='getAdverseEventMitigationById',
    )
    def get_adverse_event_mitigation_by_id(self, adverseEventId: str, mitigationId: str): # type: ignore
        return get_object_or_404(AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId)
        
    @route.post(
        path='/{adverseEventId}/mitigations', 
        response={
            201: ModifiedResourceSchema,
        },
        operation_id='createAdverseEventMitigation',
    )
    def create_adverse_event_mitigation(self, adverseEventId: str, payload: AdverseEventMitigationCreateSchema): # type: ignore
        instance = AdverseEventMitigation(adverse_event=get_object_or_404(AdverseEvent, id=adverseEventId))
        return payload.model_dump_django(instance=instance, user=self.context.request.user, create=True)

    @route.put(
        path='/{adverseEventId}/mitigations/{mitigationId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateAdverseEventMitigation',
    )
    def update_adverse_event_mitigation(self, adverseEventId: str, mitigationId: str, payload: AdverseEventMitigationCreateSchema): # type: ignore
        instance = get_object_or_404(AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
    

    @route.delete(
        path='/{adverseEventId}/mitigations/{mitigationId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteAdverseEventMitigation',
    )
    def delete_adverse_event_mitigation(self, adverseEventId: str, mitigationId: str):
        get_object_or_404(AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId).delete()
        return 204, None
    