from enum import Enum

from ninja import Query
from ninja.schema import Schema, Field
from ninja_extra.pagination import (
    paginate, 
)

from ninja_extra import (
    api_controller, 
    ControllerBase, 
    route,
)
from ninja_jwt.authentication import JWTAuth

from pop.core.schemas import ResourceIdSchema
from pop.oncology.models import NeoplasticEntity

from django.shortcuts import get_object_or_404
from typing import List
from datetime import date 

from pop.oncology.schemas import NeoplasticEntitySchema, NeoplasticEntityCreateSchema


@api_controller(
    'neoplastic-entities/', 
    auth=[JWTAuth()], 
    tags=['Neoplastic Entities'],  
)
class NeoplasticEntityController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: List[NeoplasticEntitySchema],
        },
        operation_id='getNeoplasticEntities',
    )
    def get_all_neoplastic_entities_matching_the_query(self):
        queryset = NeoplasticEntity.objects.all().order_by('-assertion_date')
        print( [NeoplasticEntitySchema.model_validate(instance) for instance in queryset])
        return 200, [NeoplasticEntitySchema.model_validate(instance) for instance in queryset]

    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema
        },
        operation_id='createNeoplasticEntity',
    )
    def create_neoplastic_entity(self, payload: NeoplasticEntityCreateSchema): # type: ignore
        instance = NeoplasticEntityCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)

    @route.get(
        path='/{entityId}', 
        response={
            200: NeoplasticEntitySchema,
            404: None,
        },
        operation_id='getNeoplasticEntityById',
    )
    def get_neoplastic_entity_by_id(self, entityId: str):
        instance = get_object_or_404(NeoplasticEntity, id=entityId)
        return 200, NeoplasticEntitySchema.model_validate(instance)

    @route.put(
        path='/{entityId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateNeoplasticEntityById',
    )
    def update_neoplastic_entity(self, entityId: str, payload: NeoplasticEntityCreateSchema): # type: ignore
        instance = get_object_or_404(NeoplasticEntity, id=entityId)
        instance = NeoplasticEntityCreateSchema\
                    .model_validate(payload.model_dump(exclude_unset=True))\
                    .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{entityId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteNeoplasticEntityById',
    )
    def delete_patient_case(self, entityId: str):
        instance = get_object_or_404(NeoplasticEntity, id=entityId)
        instance.delete()
        return 204, None
    