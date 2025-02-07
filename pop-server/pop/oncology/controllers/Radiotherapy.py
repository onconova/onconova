from typing import List

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import Radiotherapy, RadiotherapyDosage, RadiotherapySetting, TherapyLine

from django.shortcuts import get_object_or_404
from django.db import transaction

from pop.oncology.schemas import (
    RadiotherapyFilters,
    RadiotherapySchema, RadiotherapyCreateSchema, 
    RadiotherapyDosageSchema, RadiotherapyDosageCreateSchema, 
    RadiotherapySettingSchema, RadiotherapySettingCreateSchema
)

@api_controller(
    'radiotherapies', 
    auth=[JWTAuth()], 
    tags=['Radiotherapies'],  
)
class RadiotherapyController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[RadiotherapySchema],
        },
        operation_id='getRadiotherapies',
    )
    @paginate()
    def get_all_radiotherapies_matching_the_query(self, query: Query[RadiotherapyFilters]): # type: ignore
        queryset = Radiotherapy.objects.all().order_by('-period')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createRadiotherapy',
    )
    def create_radiotherapy(self, payload: RadiotherapyCreateSchema): # type: ignore
        return payload.model_dump_django(user=self.context.request.user).assign_therapy_line()
    
    @route.get(
        path='/{radiotherapyId}', 
        response={
            200: RadiotherapySchema,
            404: None,
        },
        operation_id='getRadiotherapyById',
    )
    def get_radiotherapy_by_id(self, radiotherapyId: str):
        return get_object_or_404(Radiotherapy, id=radiotherapyId)
        

    @route.delete(
        path='/{radiotherapyId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteRadiotherapyById',
    )
    def delete_radiotherapy(self, radiotherapyId: str):
        instance = get_object_or_404(Radiotherapy, id=radiotherapyId)
        case = instance.case
        instance.delete()
        TherapyLine.assign_therapy_lines(case)
        return 204, None
    
    
    @route.put(
        path='/{radiotherapyId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateRadiotherapy',
    )
    def update_radiotherapy(self, radiotherapyId: str, payload: RadiotherapyCreateSchema): # type: ignore
        instance = get_object_or_404(Radiotherapy, id=radiotherapyId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user).assign_therapy_line()
        


    @route.get(
        path='/{radiotherapyId}/dosages', 
        response={
            200: List[RadiotherapyDosageSchema],
            404: None,
        },
        operation_id='getRadiotherapyDosages',
    )
    def get_radiotherapy_dosages_matching_the_query(self, radiotherapyId: str): # type: ignore
        return get_object_or_404(Radiotherapy, id=radiotherapyId).dosages.all()


    @route.get(
        path='/{radiotherapyId}/dosages/{dosageId}', 
        response={
            200: RadiotherapyDosageSchema,
            404: None,
        },
        operation_id='getRadiotherapyDosageById',
    )
    def get_radiotherapy_dosage_by_id(self, radiotherapyId: str, dosageId: str): # type: ignore
        return get_object_or_404(RadiotherapyDosage, id=dosageId, radiotherapy__id=radiotherapyId)

    @route.post(
        path='/{radiotherapyId}/dosages', 
        response={
            201: ModifiedResourceSchema,
        },
        operation_id='createRadiotherapyDosage',
    )
    def create_radiotherapy_dosage(self, radiotherapyId: str, payload: RadiotherapyDosageCreateSchema): # type: ignore
        instance = RadiotherapyDosage(radiotherapy=get_object_or_404(Radiotherapy, id=radiotherapyId))
        return payload.model_dump_django(instance=instance, user=self.context.request.user, create=True)


    @route.put(
        path='/{radiotherapyId}/dosages/{dosageId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateRadiotherapyDosage',
    )
    def update_radiotherapy_dosage(self, radiotherapyId: str, dosageId: str, payload: RadiotherapyDosageCreateSchema): # type: ignore
        instance = get_object_or_404(RadiotherapyDosage, id=dosageId, radiotherapy__id=radiotherapyId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
        

    @route.delete(
        path='/{radiotherapyId}/dosages/{dosageId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteRadiotherapyDosage',
    )
    def delete_radiotherapy_dosage(self, radiotherapyId: str, dosageId: str):
        get_object_or_404(RadiotherapyDosage, id=dosageId, radiotherapy__id=radiotherapyId).delete()
        return 204, None
    
    
    
    
    @route.get(
        path='/{radiotherapyId}/settings', 
        response={
            200: List[RadiotherapySettingSchema],
            404: None,
        },
        operation_id='getRadiotherapySettings',
    )
    def get_radiotherapy_settings_matching_the_query(self, radiotherapyId: str): # type: ignore
        return get_object_or_404(Radiotherapy, id=radiotherapyId).settings.all()
        

    @route.get(
        path='/{radiotherapyId}/settings/{settingId}', 
        response={
            200: RadiotherapySettingSchema,
            404: None,
        },
        operation_id='getRadiotherapySettingById',
    )
    def get_radiotherapy_setting_by_id(self, radiotherapyId: str, settingId: str): # type: ignore
        return get_object_or_404(RadiotherapySetting, id=settingId, radiotherapy__id=radiotherapyId)

    @route.post(
        path='/{radiotherapyId}/settings', 
        response={
            201: ModifiedResourceSchema,
        },
        operation_id='createRadiotherapySetting',
    )
    def create_radiotherapy_setting(self, radiotherapyId: str, payload: RadiotherapySettingCreateSchema): # type: ignore
        instance = RadiotherapySetting(radiotherapy=get_object_or_404(Radiotherapy, id=radiotherapyId))
        return payload.model_dump_django(instance=instance, user=self.context.request.user, create=True)


    @route.put(
        path='/{radiotherapyId}/settings/{settingId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateRadiotherapySetting',
    )
    def update_radiotherapy_setting(self, radiotherapyId: str, settingId: str, payload: RadiotherapySettingCreateSchema): # type: ignore
        instance = get_object_or_404(RadiotherapySetting, id=settingId, radiotherapy__id=radiotherapyId)
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
    

    @route.delete(
        path='/{radiotherapyId}/settings/{settingId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteRadiotherapySetting',
    )
    def delete_radiotherapy_setting(self, radiotherapyId: str, settingId: str):
        get_object_or_404(RadiotherapySetting, id=settingId, radiotherapy__id=radiotherapyId).delete()
        return 204, None
    