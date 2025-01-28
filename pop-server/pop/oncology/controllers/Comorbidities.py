from typing import List

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import ComorbiditiesAssessment, ComorbiditiesPanel
from pop.terminology.models import ICD10Condition

from django.shortcuts import get_object_or_404
from django.db import transaction

from pop.oncology.schemas import ComorbiditiesAssessmentSchema, ComorbiditiesAssessmentCreateSchema, ComorbiditiesPanelSchema, ComorbidityPanelCategory, ComorbiditiesAssessmentFilters

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
        operation_id='getComorbiditiesAssessments',
    )
    @paginate()
    def get_all_comorbidities_assessments_matching_the_query(self, query: Query[ComorbiditiesAssessmentFilters]): # type: ignore
        queryset = ComorbiditiesAssessment.objects.all().order_by('-date')
        return [ComorbiditiesAssessmentSchema.model_validate(instance) for instance in query.apply_filters(queryset)]

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createComorbiditiesAssessment',
    )
    def create_comorbidities_assessment(self, payload: ComorbiditiesAssessmentCreateSchema): # type: ignore
        instance = ComorbiditiesAssessmentCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
        return 201, ModifiedResourceSchema(id=instance.id)
    
    @route.get(
        path='/{comorbiditiesAssessmentId}', 
        response={
            200: ComorbiditiesAssessmentSchema,
            404: None,
        },
        operation_id='getComorbiditiesAssessmentById',
    )
    def get_comorbidities_assessment_by_id(self, comorbiditiesAssessmentId: str):
        instance = get_object_or_404(ComorbiditiesAssessment, id=comorbiditiesAssessmentId)
        return 200, ComorbiditiesAssessmentSchema.model_validate(instance)

    @route.put(
        path='', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateComorbiditiesAssessment',
    )
    def update_comorbidities_assessment(self, payload: ComorbiditiesAssessmentCreateSchema): # type: ignore
        with transaction.atomic():
            instance = get_object_or_404(ComorbiditiesAssessment, id=payload.id)
            instance = ComorbiditiesAssessmentCreateSchema\
                        .model_validate(payload.model_dump(exclude_unset=True))\
                        .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{comorbiditiesAssessmentId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteComorbiditiesAssessment',
    )
    def delete_comorbidities_assessment(self, comorbiditiesAssessmentId: str):
        instance = get_object_or_404(ComorbiditiesAssessment, id=comorbiditiesAssessmentId)
        instance.delete()
        return 204, None
    
    
    @route.put(
        path='/{comorbiditiesAssessmentId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateComorbiditiesAssessment',
    )
    def update_comorbidities_assessment(self, comorbiditiesAssessmentId: str, payload: ComorbiditiesAssessmentCreateSchema): # type: ignore
        with transaction.atomic():
            instance = get_object_or_404(ComorbiditiesAssessment, id=comorbiditiesAssessmentId)
            instance = ComorbiditiesAssessmentCreateSchema\
                        .model_validate(payload.model_dump(exclude_unset=True))\
                        .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None
    

@api_controller(
    'comorbidities-panels', 
    auth=[JWTAuth()], 
    tags=['Comorbidities Assessments'],  
)
class ComorbiditiesPanelsController(ControllerBase):
    @route.get(
        path='', 
        response={
            200: List[ComorbiditiesPanelSchema], 
        },
        operation_id='getComorbiditiesPanels',
    )
    def get_all_comorbidities_panels(self): # type: ignore
        return [
            ComorbiditiesPanelSchema(name=name, categories=[
                ComorbidityPanelCategory(
                    label=category.label,
                    conditions=list(ICD10Condition.objects.filter(codes__in=category.codes))
                )
                for category in panel.categories.values()
            ])
            for name, panel in ComorbiditiesAssessment.COMORBIDITY_PANELS_DETAILS.items()
        ]
    
    @route.get(
        path='/{panel}', 
        response={
            200: ComorbiditiesPanelSchema, 
        },
        operation_id='getComorbiditiesPanelsByName',
    )
    def get_comorbidities_panel_by_name(self, panel: ComorbiditiesPanel): # type: ignore
        panel_details = ComorbiditiesAssessment.COMORBIDITY_PANELS_DETAILS.get(panel)
        if not panel_details:
            return 404
        return 200, ComorbiditiesPanelSchema(name=panel, categories=[
                ComorbidityPanelCategory(
                    label=category.label,
                    default=ICD10Condition.objects.filter(code=category.default).first(),
                    conditions=list(ICD10Condition.objects.filter(code__in=category.codes))
                )
                for category in panel_details.categories.values()
            ]
        )


