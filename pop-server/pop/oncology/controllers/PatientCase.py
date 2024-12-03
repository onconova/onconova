from enum import Enum

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ResourceIdSchema, Paginated
from pop.oncology.models import PatientCase

from django.shortcuts import get_object_or_404
from typing import List
from datetime import date 

from pop.oncology.schemas import PatientCaseSchema, PatientCaseCreateSchema

class GenderEnum(Enum):
    male = 'male'
    female = 'female'
    unknown = 'unknown'


class QueryParameters(Schema):
    db_age__lte: int = Field(None, alias='age_lte')
    db_age__gte: int = Field(None, alias='age_gte')
    pseudoidentifier__icontains: str = Field(None, alias='pseudoidentifier')
    is_deceased: bool = Field(None, alias='deceased')
    gender__code__in: List[GenderEnum] = Field(None, alias="gender")
    date_of_birth: date = Field(None, alias="born")


@api_controller(
    'patient-cases/', 
    auth=[JWTAuth()], 
    tags=['Patient Cases'],  
)
class PatientCaseController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: Paginated[PatientCaseSchema]
        },
        operation_id='getPatientCases',
    )
    @paginate()
    def get_all_patient_cases_matching_the_query(self, query: Query[QueryParameters]):
        queryset = PatientCase.objects.all().order_by('-created_at')
        for (lookup,value) in query:
            if value is not None:
                queryset = queryset.filter(**{lookup: value})
        return [PatientCaseSchema.model_validate(instance) for instance in queryset]

    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema
        },
        operation_id='createPatientCase',
    )
    def create_patient_case(self, payload: PatientCaseCreateSchema): # type: ignore
        instance = PatientCaseCreateSchema.model_validate(payload).model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)

    @route.get(
        path='/{patientId}', 
        response={
            200: PatientCaseSchema, 
            404: None
        },
        operation_id='getPatientCaseById',
        )
    def get_patient_case_by_id(self, patientId: str): 
        instance = get_object_or_404(PatientCase, id=patientId)
        return 200, PatientCaseSchema.model_validate(instance)

    @route.put(
        path='/{patientId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updatePatientCaseById',
    )
    def update_patient_case(self, patientId: str, payload: PatientCaseCreateSchema): # type: ignore
        instance = get_object_or_404(PatientCase, id=patientId)
        instance = PatientCaseCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{patientId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deletePatientCaseById',
    )
    def delete_patient_case(self, patientId: str):
        instance = get_object_or_404(PatientCase, id=patientId)
        instance.delete()
        return 204, None
    

