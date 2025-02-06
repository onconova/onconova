from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import TreatmentResponse, TherapyLine

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import TreatmentResponseSchema, TreatmentResponseCreateSchema, TreatmentResponseFilters

@api_controller(
    'treatment-responses', 
    auth=[JWTAuth()], 
    tags=['Treatment Responses'],  
)
class TreatmentResponseController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[TreatmentResponseSchema],
        },
        operation_id='getTreatmentResponses',
    )
    @paginate()
    def get_all_treatment_responses_matching_the_query(self, query: Query[TreatmentResponseFilters]): # type: ignore
        queryset = TreatmentResponse.objects.all().order_by('-date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createTreatmentResponse',
    )
    def create_treatment_response(self, payload: TreatmentResponseCreateSchema): # type: ignore
        return payload.model_dump_django(user=self.context.request.user).assign_therapy_line()

    @route.get(
        path='/{treatmentRresponseId}', 
        response={
            200: TreatmentResponseSchema,
            404: None,
        },
        operation_id='getTreatmentResponseById',
    )
    def get_treatment_response_by_id(self, treatmentRresponseId: str):
        return get_object_or_404(TreatmentResponse, id=treatmentRresponseId)


    @route.put(
        path='/{treatmentRresponseId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateTreatmentResponse',
    )
    def update_treatment_response(self, treatmentRresponseId: str, payload: TreatmentResponseCreateSchema): # type: ignore
        instance = get_object_or_404(TreatmentResponse, id=treatmentRresponseId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user).assign_therapy_line()
        
    @route.delete(
        path='/{treatmentRresponseId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteTreatmentResponse',
    )
    def delete_treatment_response(self, treatmentRresponseId: str):
        get_object_or_404(TreatmentResponse, id=treatmentRresponseId).delete()
        TherapyLine.assign_therapy_lines()
        return 204, None
    