from typing import List

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import SystemicTherapy, SystemicTherapyMedication

from django.shortcuts import get_object_or_404
from django.db import transaction

from pop.oncology.schemas import SystemicTherapySchema, SystemicTherapyCreateSchema, SystemicTherapyMedicationSchema, SystemicTherapyMedicationCreateSchema, SystemicTherapyFilters


@api_controller(
    'systemic-therapies', 
    auth=[JWTAuth()], 
    tags=['Systemic Therapies'],  
)
class SystemicTherapyController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[SystemicTherapySchema],
        },
        operation_id='getSystemicTherapies',
    )
    @paginate()
    def get_all_systemic_therapies_matching_the_query(self, query: Query[SystemicTherapyFilters]): # type: ignore
        queryset = SystemicTherapy.objects.all().order_by('-period')
        return query.apply_filters(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createSystemicTherapy',
    )
    def create_systemic_therapy(self, payload: SystemicTherapyCreateSchema): # type: ignore
        return payload.model_dump_django(user=self.context.request.user)
     
    @route.get(
        path='/{systemicTherapyId}', 
        response={
            200: SystemicTherapySchema,
            404: None,
        },
        operation_id='getSystemicTherapyById',
    )
    def get_systemic_therapy_by_id(self, systemicTherapyId: str):
        return get_object_or_404(SystemicTherapy, id=systemicTherapyId)

    @route.delete(
        path='/{systemicTherapyId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteSystemicTherapyById',
    )
    def delete_systemic_therapy(self, systemicTherapyId: str):
        get_object_or_404(SystemicTherapy, id=systemicTherapyId).delete()
        return 204, None
    
    
    @route.put(
        path='/{systemicTherapyId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateSystemicTherapy',
    )
    def update_systemic_therapy(self, systemicTherapyId: str, payload: SystemicTherapyCreateSchema): # type: ignore
        instance = get_object_or_404(SystemicTherapy, id=systemicTherapyId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
    


    @route.get(
        path='/{systemicTherapyId}/medications', 
        response={
            200: List[SystemicTherapyMedicationSchema],
            404: None,
        },
        operation_id='getSystemicTherapyMedications',
    )
    def get_systemic_therapy_medications_matching_the_query(self, systemicTherapyId: str): # type: ignore
        return get_object_or_404(SystemicTherapy, id=systemicTherapyId).medications.all()


    @route.get(
        path='/{systemicTherapyId}/medications/{medicationId}', 
        response={
            200: SystemicTherapyMedicationSchema,
            404: None,
        },
        operation_id='getSystemicTherapyMedicationById',
    )
    def get_systemic_therapy_medication_by_id(self, systemicTherapyId: str, medicationId: str): # type: ignore
        return get_object_or_404(SystemicTherapyMedication, id=medicationId, systemic_therapy__id=systemicTherapyId)

    @route.post(
        path='/{systemicTherapyId}/medications', 
        response={
            201: ModifiedResourceSchema,
        },
        operation_id='createSystemicTherapyMedication',
    )
    def create_systemic_therapy_medication(self, systemicTherapyId: str, payload: SystemicTherapyMedicationCreateSchema): # type: ignore
        instance = SystemicTherapyMedication(systemic_therapy=get_object_or_404(SystemicTherapy, id=systemicTherapyId))
        return payload.model_dump_django(instance=instance, user=self.context.request.user, create=True)
        

    @route.put(
        path='/{systemicTherapyId}/medications/{medicationId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateSystemicTherapyMedication',
    )
    def update_systemic_therapy_medication(self, systemicTherapyId: str, medicationId: str, payload: SystemicTherapyMedicationCreateSchema): # type: ignore
        instance = get_object_or_404(SystemicTherapyMedication, id=medicationId, systemic_therapy__id=systemicTherapyId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
        

    @route.delete(
        path='/{systemicTherapyId}/medications/{medicationId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteSystemicTherapyMedication',
    )
    def delete_systemic_therapy_medication(self, systemicTherapyId: str, medicationId: str):
        get_object_or_404(SystemicTherapyMedication, id=medicationId, systemic_therapy__id=systemicTherapyId).delete()
        return 204, None
    