from enum import Enum

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ResourceIdSchema, Paginated
from pop.oncology.models import PerformanceStatus

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import PerformanceStatusSchema, PerformanceStatusCreateSchema, PerformanceStatusFilters


@api_controller(
    'performance-status/', 
    auth=[JWTAuth()], 
    tags=['Performance Status'],  
)
class PerformanceStatusController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: Paginated[PerformanceStatusSchema],
        },
        operation_id='getPerformanceStatus',
    )
    @paginate()
    def get_all_performance_status_matching_the_query(self, query: Query[PerformanceStatusFilters]): # type: ignore
        queryset = PerformanceStatus.objects.all().order_by('-date')
        return [PerformanceStatusSchema.model_validate(instance) for instance in query.apply_filters(queryset)]

    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema
        },
        operation_id='createPerformanceStatus',
    )
    def create_performance_status(self, payload: PerformanceStatusCreateSchema): # type: ignore
        instance = PerformanceStatusCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)

    @route.get(
        path='/{performanceStatusId}', 
        response={
            200: PerformanceStatusSchema,
            404: None,
        },
        operation_id='getPerformanceStatusById',
    )
    def get_performance_status_by_id(self, performanceStatusId: str):
        instance = get_object_or_404(PerformanceStatus, id=performanceStatusId)
        return 200, PerformanceStatusSchema.model_validate(instance)

    @route.put(
        path='/{performanceStatusId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updatePerformanceStatusById',
    )
    def update_performance_status(self, performanceStatusId: str, payload: PerformanceStatusCreateSchema): # type: ignore
        instance = get_object_or_404(PerformanceStatus, id=performanceStatusId)
        instance = PerformanceStatusCreateSchema\
                    .model_validate(payload.model_dump(exclude_unset=True))\
                    .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{performanceStatusId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deletePerformanceStatus',
    )
    def delete_performance_status(self, performanceStatusId: str):
        instance = get_object_or_404(PerformanceStatus, id=performanceStatusId)
        instance.delete()
        return 204, None
    