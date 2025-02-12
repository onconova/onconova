from typing import List

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
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
        permissions=[perms.CanViewCases],
        operation_id='getFamilyHistories',
    )
    @paginate()
    def get_all_family_member_histories_matching_the_query(self, query: Query[FamilyHistoryFilters]): # type: ignore
        queryset = FamilyHistory.objects.all().order_by('-date')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        permissions=[perms.CanManageCases],
        operation_id='createFamilyHistory',
    )
    def create_family_history(self, payload: FamilyHistoryCreateSchema): # type: ignore
        return payload.model_dump_django(user=self.context.request.user)
        

    @route.get(
        path='/{familyHistoryId}', 
        response={
            200: FamilyHistorySchema,
            404: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getFamilyHistoryById',
    )
    def get_family_history_by_id(self, familyHistoryId: str):
        return get_object_or_404(FamilyHistory, id=familyHistoryId)
        

    @route.delete(
        path='/{familyHistoryId}', 
        response={
            204: None, 
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteFamilyHistoryById',
    )
    def delete_family_history(self, familyHistoryId: str):
        get_object_or_404(FamilyHistory, id=familyHistoryId).delete()
        return 204, None
    
    
    @route.put(
        path='/{familyHistoryId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateFamilyHistory',
    )
    def update_family_history(self, familyHistoryId: str, payload: FamilyHistoryCreateSchema): # type: ignore
        instance = get_object_or_404(FamilyHistory, id=familyHistoryId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
