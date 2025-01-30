from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import Lifestyle

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import LifestyleSchema, LifestyleCreateSchema, LifestyleFilters


@api_controller(
    'lifestyles', 
    auth=[JWTAuth()], 
    tags=['Lifestyles'],  
)
class LifestyleController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[LifestyleSchema],
        },
        operation_id='getLifestyles',
    )
    @paginate()
    def get_all_lifestyles_matching_the_query(self, query: Query[LifestyleFilters]): # type: ignore
        queryset = Lifestyle.objects.all().order_by('-date')
        return query.filter(queryset)


    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createLifestyle',
    )
    def create_lifestyle(self, payload: LifestyleCreateSchema): # type: ignore
        return payload.model_dump_django(user=self.context.request.user)
        

    @route.get(
        path='/{lifestyleId}', 
        response={
            200: LifestyleSchema,
            404: None,
        },
        operation_id='getLifestyleById',
    )
    def get_lifestyle_by_id(self, lifestyleId: str):
        return get_object_or_404(Lifestyle, id=lifestyleId)
        
        
    @route.put(
        path='/{lifestyleId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateLifestyleById',
    )
    def update_lifestyle(self, lifestyleId: str, payload: LifestyleCreateSchema): # type: ignore
        instance = get_object_or_404(Lifestyle, id=lifestyleId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
        
    @route.delete(
        path='/{lifestyleId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteLifestyleById',
    )
    def delete_lifestyle(self, lifestyleId: str):
        get_object_or_404(Lifestyle, id=lifestyleId).delete()
        return 204, None
    