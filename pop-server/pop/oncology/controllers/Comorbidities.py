from typing import List

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ResourceIdSchema, Paginated
from pop.oncology.models import ComorbiditiesAssessment

from django.shortcuts import get_object_or_404
from django.db import transaction

from pop.oncology.schemas import ComorbiditiesAssessmentSchema, ComorbiditiesAssessmentCreateSchema, ComorbiditiesPanelSchema


class QueryParameters(Schema):
    case__id: str = Field(None, alias='caseId')

@api_controller(
    'comorbidities-assessments/', 
    auth=[JWTAuth()], 
    tags=['Comorbidities Assessments'],  
)
class ComorbiditiesAssessmentController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: Paginated[ComorbiditiesAssessmentSchema],
        },
        operation_id='getComorbiditiesAssessments',
    )
    @paginate()
    def get_all_comorbidities_assessments_matching_the_query(self, query: Query[QueryParameters]):
        queryset = ComorbiditiesAssessment.objects.all().order_by('-date')
        for (lookup, value) in query:
            if value is not None:
                queryset = queryset.filter(**{lookup: value})
        return [ComorbiditiesAssessmentSchema.model_validate(instance) for instance in queryset]

    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema
        },
        operation_id='createComorbiditiesAssessment',
    )
    def create_comorbidities_assessment(self, payload: ComorbiditiesAssessmentCreateSchema): # type: ignore
        instance = ComorbiditiesAssessmentCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)
    
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
        path='/', 
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
    'comorbidities-panels/', 
    auth=[JWTAuth()], 
    tags=['Comorbidities Assessments'],  
)
class ComorbiditiesPanelsController(ControllerBase):
    @route.get(
        path='/', 
        response={
            200: List[ComorbiditiesPanelSchema], 
        },
        operation_id='getComorbiditiesPanels',
    )
    def get_all_comorbidities_panels(self): # type: ignore
        return [
            ComorbiditiesPanelSchema(name=name, categories=panel.categories.values())
            for name, panel in ComorbiditiesAssessment.COMORBIDITY_PANELS_DETAILS.items()
        ]


