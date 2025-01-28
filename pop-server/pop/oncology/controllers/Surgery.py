from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ResourceIdSchema, Paginated
from pop.oncology.models import Surgery

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import SurgerySchema, SurgeryCreateSchema, SurgeryFilters

@api_controller(
    'surgeries/', 
    auth=[JWTAuth()], 
    tags=['Surgeries'],  
)
class SurgeryController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: Paginated[SurgerySchema],
        },
        operation_id='getSurgeries',
    )
    @paginate()
    def get_all_surgeries_matching_the_query(self, query: Query[SurgeryFilters]): # type: ignore
        queryset = Surgery.objects.all().order_by('-date')
        return [SurgerySchema.model_validate(instance) for instance in query.apply_filters(queryset)]

    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema
        },
        operation_id='createSurgery',
    )
    def create_surgery(self, payload: SurgeryCreateSchema): # type: ignore
        instance = SurgeryCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)

    @route.get(
        path='/{surgeryId}', 
        response={
            200: SurgerySchema,
            404: None,
        },
        operation_id='getSurgeryById',
    )
    def get_surgery_by_id(self, surgeryId: str):
        instance = get_object_or_404(Surgery, id=surgeryId)
        return 200, SurgerySchema.model_validate(instance)

    @route.put(
        path='/{surgeryId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateSurgeryById',
    )
    def update_surgery(self, surgeryId: str, payload: SurgeryCreateSchema): # type: ignore
        instance = get_object_or_404(Surgery, id=surgeryId)
        instance = SurgeryCreateSchema\
                    .model_validate(payload.model_dump(exclude_unset=True))\
                    .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{surgeryId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteSurgeryById',
    )
    def delete_surgery(self, surgeryId: str):
        instance = get_object_or_404(Surgery, id=surgeryId)
        instance.delete()
        return 204, None
    