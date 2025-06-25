import pghistory

from ninja import Query
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth
from pop.core.anonymization import anonymize
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema, Paginated
from pop.core.history.schemas import HistoryEvent
from pop.oncology.models import TreatmentResponse, TherapyLine

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import (
    TreatmentResponseSchema,
    TreatmentResponseCreateSchema,
    TreatmentResponseFilters,
)


@api_controller(
    "treatment-responses",
    auth=[XSessionTokenAuth()],
    tags=["Treatment Responses"],
)
class TreatmentResponseController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[TreatmentResponseSchema],
        },
        permissions=[perms.CanViewCases],
        operation_id="getTreatmentResponses",
    )
    @paginate()
    @anonymize()
    def get_all_treatment_responses_matching_the_query(self, query: Query[TreatmentResponseFilters], anonymized: bool = True):  # type: ignore
        queryset = TreatmentResponse.objects.all().order_by("-date")
        return query.filter(queryset)

    @route.post(
        path="",
        response={
            201: ModifiedResourceSchema,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="createTreatmentResponse",
    )
    def create_treatment_response(self, payload: TreatmentResponseCreateSchema):  # type: ignore
        return 201, payload.model_dump_django().assign_therapy_line()

    @route.get(
        path="/{treatmentRresponseId}",
        response={
            200: TreatmentResponseSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getTreatmentResponseById",
    )
    @anonymize()
    def get_treatment_response_by_id(
        self, treatmentRresponseId: str, anonymized: bool = True
    ):
        return get_object_or_404(TreatmentResponse, id=treatmentRresponseId)

    @route.put(
        path="/{treatmentRresponseId}",
        response={
            200: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateTreatmentResponse",
    )
    def update_treatment_response(self, treatmentRresponseId: str, payload: TreatmentResponseCreateSchema):  # type: ignore
        instance = get_object_or_404(TreatmentResponse, id=treatmentRresponseId)
        return payload.model_dump_django(instance=instance).assign_therapy_line()

    @route.delete(
        path="/{treatmentRresponseId}",
        response={
            204: None,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteTreatmentResponse",
    )
    def delete_treatment_response(self, treatmentRresponseId: str):
        instance = get_object_or_404(TreatmentResponse, id=treatmentRresponseId)
        case = instance.case
        instance.delete()
        TherapyLine.assign_therapy_lines(case)
        return 204, None

    @route.get(
        path="/{treatmentRresponseId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(TreatmentResponseCreateSchema)],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllTreatmentResponseHistoryEvents",
    )
    @paginate()
    def get_all_treatment_response_history_events(self, treatmentRresponseId: str):
        instance = get_object_or_404(TreatmentResponse, id=treatmentRresponseId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{treatmentRresponseId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(TreatmentResponseCreateSchema),
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getTreatmentResponseHistoryEventById",
    )
    def get_treatment_response_history_event_by_id(
        self, treatmentRresponseId: str, eventId: str
    ):
        instance = get_object_or_404(TreatmentResponse, id=treatmentRresponseId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{treatmentRresponseId}/history/events/{eventId}/reversion",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="revertTreatmentResponseToHistoryEvent",
    )
    def revert_treatment_response_to_history_event(
        self, treatmentRresponseId: str, eventId: str
    ):
        instance = get_object_or_404(TreatmentResponse, id=treatmentRresponseId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
