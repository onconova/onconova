import pghistory 
import dataclasses
from typing import List

from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
from pop.core.schemas import ModifiedResourceSchema, Paginated, HistoryEvent
from pop.oncology.models import ComorbiditiesAssessment, ComorbiditiesPanel
from pop.oncology.models.comorbidities import ComorbidityPanelCategory as ComorbidityPanelCategoryType
from pop.terminology.models import ICD10Condition

from django.shortcuts import get_object_or_404
from django.db import transaction

from pop.oncology.schemas import ComorbiditiesAssessmentSchema, ComorbiditiesAssessmentCreateSchema, ComorbiditiesPanel, ComorbidityPanelCategory, ComorbiditiesAssessmentFilters

@api_controller(
    'comorbidities-assessments', 
    auth=[JWTAuth()], 
    tags=['Comorbidities Assessments'],  
)
class ComorbiditiesAssessmentController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[ComorbiditiesAssessmentSchema],
        },
        permissions=[perms.CanViewCases],
        operation_id='getComorbiditiesAssessments',
    )
    @paginate()
    def get_all_comorbidities_assessments_matching_the_query(self, query: Query[ComorbiditiesAssessmentFilters]): # type: ignore
        queryset = ComorbiditiesAssessment.objects.all().order_by('-date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='createComorbiditiesAssessment',
    )
    def create_comorbidities_assessment(self, payload: ComorbiditiesAssessmentCreateSchema): # type: ignore
        return 201, payload.model_dump_django()
        
    @route.get(
        path='/{comorbiditiesAssessmentId}', 
        response={
            200: ComorbiditiesAssessmentSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getComorbiditiesAssessmentById',
    )
    def get_comorbidities_assessment_by_id(self, comorbiditiesAssessmentId: str):
        return get_object_or_404(ComorbiditiesAssessment, id=comorbiditiesAssessmentId)
        

    @route.delete(
        path='/{comorbiditiesAssessmentId}', 
        response={
            204: None, 
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteComorbiditiesAssessment',
    )
    def delete_comorbidities_assessment(self, comorbiditiesAssessmentId: str):
        instance = get_object_or_404(ComorbiditiesAssessment, id=comorbiditiesAssessmentId)
        instance.delete()
        return 204, None
    
    
    @route.put(
        path='/{comorbiditiesAssessmentId}', 
       response={
            200: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateComorbiditiesAssessment',
    )
    def update_comorbidities_assessment(self, comorbiditiesAssessmentId: str, payload: ComorbiditiesAssessmentCreateSchema): # type: ignore
        with transaction.atomic():
            instance = get_object_or_404(ComorbiditiesAssessment, id=comorbiditiesAssessmentId)
            return ComorbiditiesAssessmentCreateSchema\
                        .model_validate(payload.model_dump(exclude_unset=True))\
                        .model_dump_django(instance=instance)
    
    @route.get(
        path='/{comorbiditiesAssessmentId}/history/events', 
        response={
            200: Paginated[HistoryEvent],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllComorbiditiesAssessmentHistoryEvents',
    )
    @paginate()
    def get_all_comorbidities_assessment_history_events(self, comorbiditiesAssessmentId: str):
        instance = get_object_or_404(ComorbiditiesAssessment, id=comorbiditiesAssessmentId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path='/{comorbiditiesAssessmentId}/history/events/{eventId}', 
        response={
            200: HistoryEvent,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getComorbiditiesAssessmentHistoryEventById',
    )
    def get_comorbidities_assessment_history_event_by_id(self, comorbiditiesAssessmentId: str, eventId: str):
        instance = get_object_or_404(ComorbiditiesAssessment, id=comorbiditiesAssessmentId)
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)

    @route.put(
        path='/{comorbiditiesAssessmentId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertComorbiditiesAssessmentToHistoryEvent',
    )
    def revert_comorbidities_assessment_to_history_event(self, comorbiditiesAssessmentId: str, eventId: str):
        instance = get_object_or_404(ComorbiditiesAssessment, id=comorbiditiesAssessmentId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.get(
        path='/meta/panels', 
        response={
            200: List[ComorbiditiesPanel], 
            401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getComorbiditiesPanels',
    )
    def get_all_comorbidities_panels(self): # type: ignore
        return [
            ComorbiditiesPanel(name=name, categories=[
                ComorbidityPanelCategory(
                    label=category.label,
                    conditions=list(ICD10Condition.objects.filter(code__in=category.codes))
                )
                for category in  [category for category in panel.__dict__.values() if isinstance(category, ComorbidityPanelCategoryType)]
            ])
            for name, panel in ComorbiditiesAssessment.COMORBIDITY_PANELS_DETAILS.items()
        ]
    
    @route.get(
        path='/meta/panels/{panel}', 
        response={
            200: ComorbiditiesPanel, 
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getComorbiditiesPanelsByName',
    )
    def get_comorbidities_panel_by_name(self, panel: str):
        panel_details = ComorbiditiesAssessment.COMORBIDITY_PANELS_DETAILS.get(panel)
        if not panel_details:
            return 404
        panel_categories = [category for category in panel_details.__dict__.values() if isinstance(category, ComorbidityPanelCategoryType)]
        return 200, ComorbiditiesPanel(name=panel, categories=[
                ComorbidityPanelCategory(
                    label=category.label,
                    default=ICD10Condition.objects.filter(code=category.default).first(),
                    conditions=list(ICD10Condition.objects.filter(code__in=category.codes))
                )
                for category in panel_categories
            ]
        )


