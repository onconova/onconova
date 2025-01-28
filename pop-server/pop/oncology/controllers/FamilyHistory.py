from typing import List

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import FamilyHistory

from django.shortcuts import get_object_or_404
from django.db import transaction

from pop.oncology.schemas import FamilyHistorySchema, FamilyHistoryCreateSchema, FamilyHistoryFilters

@api_controller(
    'family-histories', 
    auth=[JWTAuth()], 
    tags=['Family Histories'],  
)
class FamilyHistoryController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[FamilyHistorySchema],
        },
        operation_id='getFamilyHistories',
    )
    @paginate()
    def get_all_family_member_histories_matching_the_query(self, query: Query[FamilyHistoryFilters]): # type: ignore
        queryset = FamilyHistory.objects.all().order_by('-date')
        return [FamilyHistorySchema.model_validate(instance) for instance in query.apply_filters(queryset)]

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createFamilyHistory',
    )
    def create_family_history(self, payload: FamilyHistoryCreateSchema): # type: ignore
        instance = FamilyHistoryCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
        return 201, ModifiedResourceSchema(id=instance.id)
    
    @route.get(
        path='/{familyHistoryId}', 
        response={
            200: FamilyHistorySchema,
            404: None,
        },
        operation_id='getFamilyHistoryById',
    )
    def get_family_history_by_id(self, familyHistoryId: str):
        instance = get_object_or_404(FamilyHistory, id=familyHistoryId)
        return 200, FamilyHistorySchema.model_validate(instance)

    @route.put(
        path='', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateFamilyHistory',
    )
    def update_family_history(self, payload: FamilyHistoryCreateSchema): # type: ignore
        with transaction.atomic():
            instance = get_object_or_404(FamilyHistory, id=payload.id)
            instance = FamilyHistoryCreateSchema\
                        .model_validate(payload.model_dump(exclude_unset=True))\
                        .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{familyHistoryId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteFamilyHistoryById',
    )
    def delete_family_history(self, familyHistoryId: str):
        instance = get_object_or_404(FamilyHistory, id=familyHistoryId)
        instance.delete()
        return 204, None
    
    
    @route.put(
        path='/{familyHistoryId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateFamilyHistory',
    )
    def update_family_history(self, familyHistoryId: str, payload: FamilyHistoryCreateSchema): # type: ignore
        with transaction.atomic():
            instance = get_object_or_404(FamilyHistory, id=familyHistoryId)
            instance = FamilyHistoryCreateSchema\
                        .model_validate(payload.model_dump(exclude_unset=True))\
                        .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None
    
