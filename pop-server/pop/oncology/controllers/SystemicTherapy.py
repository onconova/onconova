from enum import Enum

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ResourceIdSchema, Paginated
from pop.oncology.models import SystemicTherapy

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import SystemicTherapySchema, SystemicTherapyCreateSchema


class QueryParameters(Schema):
    case__id: str = Field(None, alias='caseId')

@api_controller(
    'systemic-therapies/', 
    auth=[JWTAuth()], 
    tags=['Systemic Therapies'],  
)
class SystemicTherapyController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: Paginated[SystemicTherapySchema],
        },
        operation_id='getSystemicTherapies',
    )
    @paginate()
    def get_all_systemic_therapies_matching_the_query(self, query: Query[QueryParameters]):
        queryset = SystemicTherapy.objects.all().order_by('-period')
        for (lookup, value) in query:
            if value is not None:
                queryset = queryset.filter(**{lookup: value})
        return [SystemicTherapySchema.model_validate(instance) for instance in queryset]

    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema
        },
        operation_id='createSystemicTherapy',
    )
    def create_systemic_therapy(self, payload: SystemicTherapyCreateSchema): # type: ignore
        instance = SystemicTherapyCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)

    @route.get(
        path='/{systemicTherapyId}', 
        response={
            200: SystemicTherapySchema,
            404: None,
        },
        operation_id='getSystemicTherapyById',
    )
    def get_systemic_therapy_by_id(self, systemicTherapyId: str):
        instance = get_object_or_404(SystemicTherapy, id=systemicTherapyId)
        return 200, SystemicTherapySchema.model_validate(instance)

    @route.put(
        path='/{systemicTherapyId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateSystemicTherapyById',
    )
    def update_systemic_therapy(self, systemicTherapyId: str, payload: SystemicTherapyCreateSchema): # type: ignore
        instance = get_object_or_404(SystemicTherapy, id=systemicTherapyId)
        instance = SystemicTherapyCreateSchema\
                    .model_validate(payload.model_dump(exclude_unset=True))\
                    .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{systemicTherapyId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteSystemicTherapyById',
    )
    def delete_systemic_therapy(self, systemicTherapyId: str):
        instance = get_object_or_404(SystemicTherapy, id=systemicTherapyId)
        instance.delete()
        return 204, None
    