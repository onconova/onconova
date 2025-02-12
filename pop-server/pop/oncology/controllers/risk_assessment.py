from enum import Enum

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import RiskAssessment

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import RiskAssessmentSchema, RiskAssessmentCreateSchema, RiskAssessmentFilters


@api_controller(
    'risk-assessments', 
    auth=[JWTAuth()], 
    tags=['Risk Assessments'],  
)
class RiskAssessmentController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[RiskAssessmentSchema],
        },
        permissions=[perms.CanViewCases],
        operation_id='getRiskAssessments',
    )
    @paginate()
    def get_all_risk_assessments_matching_the_query(self, query: Query[RiskAssessmentFilters]): # type: ignore
        queryset = RiskAssessment.objects.all().order_by('-date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        permissions=[perms.CanManageCases],
        operation_id='createRiskAssessment',
    )
    def create_risk_assessment(self, payload: RiskAssessmentCreateSchema): # type: ignore
        return payload.model_dump_django(user=self.context.request.user)

    @route.get(
        path='/{riskAssessmentId}', 
        response={
            200: RiskAssessmentSchema,
            404: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getRiskAssessmentById',
    )
    def get_risk_assessment_by_id(self, riskAssessmentId: str):
        return get_object_or_404(RiskAssessment, id=riskAssessmentId)

    @route.put(
        path='/{riskAssessmentId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateRiskAssessmentById',
    )
    def update_risk_assessment(self, riskAssessmentId: str, payload: RiskAssessmentCreateSchema): # type: ignore
        instance = get_object_or_404(RiskAssessment, id=riskAssessmentId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)

    @route.delete(
        path='/{riskAssessmentId}', 
        response={
            204: None, 
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteRiskAssessmentById',
    )
    def delete_risk_assessment(self, riskAssessmentId: str):
        get_object_or_404(RiskAssessment, id=riskAssessmentId).delete()
        return 204, None
    