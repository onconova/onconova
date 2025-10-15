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
    models as orm,
    schemas as scm,
)


@api_controller(
    "risk-assessments",
    auth=[XSessionTokenAuth()],
    tags=["Risk Assessments"],
)
class RiskAssessmentController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[scm.RiskAssessment],
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getRiskAssessments",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_risk_assessments_matching_the_query(self, query: Query[scm.RiskAssessmentFilters]):  # type: ignore
        queryset = orm.RiskAssessment.objects.all().order_by("-date")
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createRiskAssessment",
    )
    def create_risk_assessment(self, payload: scm.RiskAssessmentCreate): 
        return 201, payload.model_dump_django()

    @route.get(
        path="/{riskAssessmentId}",
        response={200: scm.RiskAssessment, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getRiskAssessmentById",
    )
    @anonymize()
    def get_risk_assessment_by_id(self, riskAssessmentId: str):
        return get_object_or_404(orm.RiskAssessment, id=riskAssessmentId)

    @route.put(
        path="/{riskAssessmentId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateRiskAssessmentById",
    )
    def update_risk_assessment(self, riskAssessmentId: str, payload: scm.RiskAssessmentCreate): 
        instance = get_object_or_404(orm.RiskAssessment, id=riskAssessmentId)
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{riskAssessmentId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteRiskAssessmentById",
    )
    def delete_risk_assessment(self, riskAssessmentId: str):
        get_object_or_404(orm.RiskAssessment, id=riskAssessmentId).delete()
        return 204, None

    @route.get(
        path="/{riskAssessmentId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(scm.RiskAssessmentCreate)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllRiskAssessmentHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_risk_assessment_history_events(self, riskAssessmentId: str):
        instance = get_object_or_404(orm.RiskAssessment, id=riskAssessmentId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{riskAssessmentId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.RiskAssessmentCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getRiskAssessmentHistoryEventById",
    )
    def get_risk_assessment_history_event_by_id(
        self, riskAssessmentId: str, eventId: str
    ):
        instance = get_object_or_404(orm.RiskAssessment, id=riskAssessmentId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{riskAssessmentId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertRiskAssessmentToHistoryEvent",
    )
    def revert_risk_assessment_to_history_event(
        self, riskAssessmentId: str, eventId: str
    ):
        instance = get_object_or_404(orm.RiskAssessment, id=riskAssessmentId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()