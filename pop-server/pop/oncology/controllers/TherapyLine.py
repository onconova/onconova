from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route
from typing import List
from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import TherapyLine, PatientCase

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import TherapyLineSchema, TherapyLineCreateSchema, TherapyLineFilters

@api_controller(
    'therapy-lines', 
    auth=[JWTAuth()], 
    tags=['Therapy Lines'],  
)
class TherapyLineController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[TherapyLineSchema],
        },
        operation_id='getTherapyLines',
    )
    @paginate()
    def get_all_therapy_lines_matching_the_query(self, query: Query[TherapyLineFilters]): # type: ignore
        queryset = TherapyLine.objects.all().order_by('-period')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createTherapyLine',
    )
    def create_therapy_line(self, payload: TherapyLineCreateSchema): # type: ignore
        return payload.model_dump_django(user=self.context.request.user)

    @route.get(
        path='/{therapyLineId}', 
        response={
            200: TherapyLineSchema,
            404: None,
        },
        operation_id='getTherapyLineById',
    )
    def get_therapy_line_by_id(self, therapyLineId: str):
        return get_object_or_404(TherapyLine, id=therapyLineId)


    @route.put(
        path='/{therapyLineId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateTherapyLine',
    )
    def update_therapy_line(self, therapyLineId: str, payload: TherapyLineCreateSchema): # type: ignore
        instance = get_object_or_404(TherapyLine, id=therapyLineId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
        
    @route.delete(
        path='/{therapyLineId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteTherapyLine',
    )
    def delete_therapy_line(self, therapyLineId: str):
        get_object_or_404(TherapyLine, id=therapyLineId).delete()
        return 204, None
    
    
    @route.get(
        path='/{caseId}/re-assignments', 
        response={
            200: List[TherapyLineSchema],
            404: None,
        },
        operation_id='getReassignedPatientCaseTherapyLines',
    )
    def get_reassigned_patient_case_therapy_lines(self, caseId: str):
        return TherapyLine.assign_therapy_lines(get_object_or_404(PatientCase, id=caseId))
