from ninja import NinjaAPI, Redoc, Swagger
from pop.core.models import CancerPatient
from pop.core.schemas.factory import create_schema
from django.shortcuts import get_object_or_404
from typing import List

api = NinjaAPI(docs=Swagger(settings={'showExtensions': True}))


CancerPatientSchema = create_schema(CancerPatient)

@api.get("/cancer-patients", response=List[CancerPatientSchema])
def get_all_cancer_patient_matching_the_query(request, id: str):
    return CancerPatient.objects.get(id=id)

@api.post("/cancer-patients", response=CancerPatientSchema)
def create_cancer_patient(request, payload):
    patient = CancerPatient.objects.create(**payload.dict())
    return {"id": patient.id}

@api.get("/cancer-patients/{id}", response=CancerPatientSchema)
def get_cancer_patient_by_id(request, id: str):
    return CancerPatient.objects.get(id=id)


@api.put("/cancer-patients/{id}")
def update_cancer_patient_by_id(request, id: str, payload):
    patient = get_object_or_404(CancerPatient, id=id)
    for attr, value in payload.dict().items():
        setattr(patient, attr, value)
    patient.save()
    return {"success": True}

@api.delete("/cancer-patients/{id}")
def delete_cancer_patient_by_id(request, id: str):
    patient = get_object_or_404(CancerPatient, id=id)
    patient.delete()
    return {"success": True}

