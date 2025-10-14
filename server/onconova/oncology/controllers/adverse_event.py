from typing import List

import pghistory
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate

from onconova.core.anonymization import anonymize
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.history.schemas import HistoryEvent
from onconova.core.schemas import ModifiedResource as ModifiedResourceSchema
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.oncology import (
    schemas as scm,
    models as orm,
)

@api_controller(
    "adverse-events",
    auth=[XSessionTokenAuth()],
    tags=["Adverse Events"],
)
class AdverseEventController(ControllerBase):

    @route.get(
        path="",
        response={200: Paginated[scm.AdverseEvent], **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getAdverseEvents",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_adverse_events_matching_the_query(self, query: Query[scm.AdverseEventFilters]): # type: ignore 
        queryset = orm.AdverseEvent.objects.all()
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createAdverseEvent",
    )
    def create_adverse_event(self, payload: scm.AdverseEventCreate):  
        return 201, scm.AdverseEventCreate.model_validate(payload).model_dump_django()

    @route.get(
        path="/{adverseEventId}",
        response={200: scm.AdverseEvent, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getAdverseEventById",
    )
    @anonymize()
    def get_adverse_event_by_id(self, adverseEventId: str):
        return get_object_or_404(orm.AdverseEvent, id=adverseEventId)

    @route.delete(
        path="/{adverseEventId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteAdverseEventById",
    )
    def delete_adverse_event(self, adverseEventId: str):
        get_object_or_404(orm.AdverseEvent, id=adverseEventId).delete()
        return 204, None

    @route.put(
        path="/{adverseEventId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateAdverseEvent",
    )
    def update_adverse_event(self, adverseEventId: str, payload: scm.AdverseEventCreate):  
        instance = get_object_or_404(orm.AdverseEvent, id=adverseEventId)
        return payload.model_dump_django(instance=instance)

    @route.get(
        path="/{adverseEventId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(scm.AdverseEventCreate)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllAdverseEventHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_adverse_event_history_events(self, adverseEventId: str):
        instance = get_object_or_404(orm.AdverseEvent, id=adverseEventId)
        return pghistory.models.Events.objects.tracks(instance).all()   

    @route.get(
        path="/{adverseEventId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.AdverseEventCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAdverseEventHistoryEventById",
    )
    def get_adverse_event_history_event_by_id(self, adverseEventId: str, eventId: str):
        instance = get_object_or_404(orm.AdverseEvent, id=adverseEventId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  
        )

    @route.put(
        path="/{adverseEventId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertAdverseEventToHistoryEvent",
    )
    def revert_adverse_event_to_history_event(self, adverseEventId: str, eventId: str):
        instance = get_object_or_404(orm.AdverseEvent, id=adverseEventId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.get(
        path="/{adverseEventId}/suspected-causes",
        response={
            200: List[scm.AdverseEventSuspectedCause],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAdverseEventSuspectedCauses",
    )
    def get_adverse_event_suspected_causes_matching_the_query(
        self, adverseEventId: str
    ):
        return get_object_or_404(orm.AdverseEvent, id=adverseEventId).suspected_causes.all()  

    @route.get(
        path="/{adverseEventId}/suspected-causes/{causeId}",
        response={
            200: scm.AdverseEventSuspectedCause,
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAdverseEventSuspectedCauseById",
    )
    def get_adverse_event_suspected_cause_by_id(
        self, adverseEventId: str, causeId: str
    ):
        return get_object_or_404(
            orm.AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId
        )

    @route.post(
        path="/{adverseEventId}/suspected-causes",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createAdverseEventSuspectedCause",
    )
    def create_adverse_event_suspected_cause(self, adverseEventId: str, payload: scm.AdverseEventSuspectedCauseCreate):  
        instance = orm.AdverseEventSuspectedCause(
            adverse_event=get_object_or_404(orm.AdverseEvent, id=adverseEventId)
        )
        return 201, payload.model_dump_django(instance=instance, create=True)

    @route.put(
        path="/{adverseEventId}/suspected-causes/{causeId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateAdverseEventSuspectedCause",
    )
    def update_adverse_event_suspected_cause(self, adverseEventId: str, causeId: str, payload: scm.AdverseEventSuspectedCauseCreate):  
        instance = get_object_or_404(
            orm.AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId
        )
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{adverseEventId}/suspected-causes/{causeId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteAdverseEventSuspectedCause",
    )
    def delete_adverse_event_suspected_cause(self, adverseEventId: str, causeId: str):
        get_object_or_404(
            orm.AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId
        ).delete()
        return 204, None

    @route.get(
        path="/{adverseEventId}/suspected-causes/{causeId}/history/events",
        response={
            200: Paginated[
                HistoryEvent.bind_schema(scm.AdverseEventSuspectedCauseCreate)
            ],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllAdverseEventSuspectedCauseHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_adverse_event_suspected_cause_history_events(
        self, adverseEventId: str, causeId: str
    ):
        instance = get_object_or_404(
            orm.AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId
        )
        return pghistory.models.Events.objects.tracks(instance).all()  

    @route.get(
        path="/{adverseEventId}/suspected-causes/{causeId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.AdverseEventSuspectedCauseCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAdverseEventSuspectedCauseHistoryEventById",
    )
    def get_adverse_event_suspected_cause_history_event_by_id(
        self, adverseEventId: str, causeId: str, eventId: str
    ):
        instance = get_object_or_404(
            orm.AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId
        )
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId   
        )

    @route.put(
        path="/{adverseEventId}/suspected-causes/{causeId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertAdverseEventSuspectedCauseToHistoryEvent",
    )
    def revert_adverse_event_suspected_cause_to_history_event(
        self, adverseEventId: str, causeId: str, eventId: str
    ):
        instance = get_object_or_404(
            orm.AdverseEventSuspectedCause, id=causeId, adverse_event__id=adverseEventId
        )
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.get(
        path="/{adverseEventId}/mitigations",
        response={
            200: List[scm.AdverseEventMitigation],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAdverseEventMitigations",
    )
    def get_adverse_event_mitigations_matching_the_query(self, adverseEventId: str):
        return get_object_or_404(orm.AdverseEvent, id=adverseEventId).mitigations.all() 

    @route.get(
        path="/{adverseEventId}/mitigations/{mitigationId}",
        response={200: scm.AdverseEventMitigation, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getAdverseEventMitigationById",
    )
    def get_adverse_event_mitigation_by_id(
        self, adverseEventId: str, mitigationId: str
    ):
        return get_object_or_404(
            orm.AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId
        )

    @route.post(
        path="/{adverseEventId}/mitigations",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createAdverseEventMitigation",
    )
    def create_adverse_event_mitigation(self, adverseEventId: str, payload: scm.AdverseEventMitigationCreate):  
        instance = orm.AdverseEventMitigation(
            adverse_event=get_object_or_404(orm.AdverseEvent, id=adverseEventId)
        )
        return 201, payload.model_dump_django(instance=instance, create=True)

    @route.put(
        path="/{adverseEventId}/mitigations/{mitigationId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateAdverseEventMitigation",
    )
    def update_adverse_event_mitigation(self, adverseEventId: str, mitigationId: str, payload: scm.AdverseEventMitigationCreate):  
        instance = get_object_or_404(
            orm.AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId
        )
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{adverseEventId}/mitigations/{mitigationId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteAdverseEventMitigation",
    )
    def delete_adverse_event_mitigation(self, adverseEventId: str, mitigationId: str):
        get_object_or_404(
            orm.AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId
        ).delete()
        return 204, None

    @route.get(
        path="/{adverseEventId}/mitigations/{mitigationId}/history/events",
        response={
            200: Paginated[
                HistoryEvent.bind_schema(scm.AdverseEventMitigationCreate)
            ],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllAdverseEventMitigationHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_adverse_event_mitigation_history_events(
        self, adverseEventId: str, mitigationId: str
    ):
        instance = get_object_or_404(
            orm.AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId
        )
        return pghistory.models.Events.objects.tracks(instance).all()  

    @route.get(
        path="/{adverseEventId}/mitigations/{mitigationId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.AdverseEventMitigationCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAdverseEventMitigationHistoryEventById",
    )
    def get_adverse_event_mitigation_history_event_by_id(
        self, adverseEventId: str, mitigationId: str, eventId: str
    ):
        instance = get_object_or_404(
            orm.AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId
        )
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  
        )

    @route.put(
        path="/{adverseEventId}/mitigations/{mitigationId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertAdverseEventMitigationToHistoryEvent",
    )
    def revert_adverse_event_mitigation_to_history_event(
        self, adverseEventId: str, mitigationId: str, eventId: str
    ):
        instance = get_object_or_404(
            orm.AdverseEventMitigation, id=mitigationId, adverse_event__id=adverseEventId
        )
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()