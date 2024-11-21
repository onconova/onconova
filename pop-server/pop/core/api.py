from ninja import NinjaAPI, Redoc, Swagger, Query
from ninja.schema import Schema, Field

from enum import Enum

from pop.core.models import CancerPatient
from pop.core.schemas.factory import create_schema, BaseSchema
from django.shortcuts import get_object_or_404
from typing import List
from datetime import date 

api = NinjaAPI(
    docs=Swagger(settings={'showExtensions': True})
)


CancerPatientIn: BaseSchema = create_schema(
    model=CancerPatient, 
    name='CancerPatientIn', 
    exclude=('id', 'created_at', 'updated_at', 'pseudoidentifier')
)
CancerPatientOut: BaseSchema = create_schema(
    model=CancerPatient,
    name='CancerPatientOut', 
)


class GenderEnum(Enum):
    male = 'male'
    female = 'female'
    unknown = 'unknown'


class Filters(Schema):
    pseudoidentifier__icontains: str = Field(None, alias='pseudoidentifier')
    is_deceased: bool = Field(None, alias='deceased')
    gender__code__in: List[GenderEnum] = Field(None, alias="gender")
    birthdate: date = Field(None, alias="born")

@api.get("/cancer-patients", response=List[CancerPatientOut])
def get_all_cancer_patient_matching_the_query(request, filters: Query[Filters]):
    queryset = CancerPatient.objects.all()
    for (filter,value) in filters:
        if value is not None:
            queryset = queryset.filter(**{filter: value})
    return queryset

@api.post("/cancer-patients")
def create_cancer_patient(request, payload: CancerPatientIn): # type: ignore
    instance = CancerPatientIn.model_validate(payload).model_dump_django(save=True)
    return {"id": instance.id}

@api.get("/cancer-patients/{id}", response=CancerPatientOut)
def get_cancer_patient_by_id(request, id: str):
    return CancerPatient.objects.get(id=id)

@api.put("/cancer-patients/{id}")
def update_cancer_patient_by_id(request, id: str, payload: CancerPatientIn): # type: ignore
    instance = get_object_or_404(CancerPatient, id=id)
    instance = CancerPatientIn.model_validate(payload).model_dump_django(instance=instance, save=True)
    return {"success": True}

@api.delete("/cancer-patients/{id}")
def delete_cancer_patient_by_id(request, id: str):
    get_object_or_404(CancerPatient, id=id).delete()
    return {"success": True}

