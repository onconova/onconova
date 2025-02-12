from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import Vitals

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import VitalsSchema, VitalsCreateSchema, VitalsFilters

@api_controller(
    'vitals', 
    auth=[JWTAuth()], 
    tags=['Vitals'],  
)
class VitalsController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[VitalsSchema],
        },
        permissions=[perms.CanViewCases],
        operation_id='getVitals',
    )
    @paginate()
    def get_all_vitals_matching_the_query(self, query: Query[VitalsFilters]): # type: ignore
        queryset = Vitals.objects.all().order_by('-date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        permissions=[perms.CanManageCases],
        operation_id='createVitals',
    )
    def create_vitals(self, payload: VitalsCreateSchema): # type: ignore
        return payload.model_dump_django(user=self.context.request.user)
        
        
    @route.get(
        path='/{vitalsId}', 
        response={
            200: VitalsSchema,
            404: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getVitalsById',
    )
    def get_vitals_by_id(self, vitalsId: str):
        return get_object_or_404(Vitals, id=vitalsId)
        
        
    @route.put(
        path='/{vitalsId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateVitalsById',
    )
    def update_vitals(self, vitalsId: str, payload: VitalsCreateSchema): # type: ignore
        instance = get_object_or_404(Vitals, id=vitalsId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
        
        
    @route.delete(
        path='/{vitalsId}', 
        response={
            204: None, 
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteVitalsById',
    )
    def delete_vitals(self, vitalsId: str):
        get_object_or_404(Vitals, id=vitalsId).delete()
        return 204, None
    