from ninja import NinjaAPI, Redoc, Swagger
from pop.core.models import CancerPatient
from pop.core.models.fields import SingleCodedConceptField, MultipleCodedConceptField 
from pop.terminology.models import CodedConcept
from django.shortcuts import get_object_or_404
from django.core.exceptions import FieldDoesNotExist
from typing import List, Optional

api = NinjaAPI(docs=Swagger())

from ninja import ModelSchema,Schema

class CodedConceptSchema(Schema):
    code: str 
    display: str
    system: str
    version: Optional[str] = None
    synonyms: Optional[List[str]] = None
    properties: Optional[dict] = None


class CancerPatientSchema(ModelSchema):
    class Meta:
        model = CancerPatient
        exclude = ['auto_id']

@api.get("/cancer-patients", response=List[CancerPatientSchema])
def get_all_cancer_patient_matching_the_query(request, id: str):
    return CancerPatient.objects.get(id=id)

@api.post("/cancer-patients", response=CancerPatientSchema)
def create_cancer_patient(request, payload: CancerPatientSchema):
    patient = CancerPatient.objects.create(**payload.dict())
    return {"id": patient.id}

@api.get("/cancer-patients/{id}", response=CancerPatientSchema)
def get_cancer_patient_by_id(request, id: str):
    return CancerPatient.objects.get(id=id)


@api.put("/cancer-patients/{id}")
def update_cancer_patient_by_id(request, id: str, payload: CancerPatientSchema):
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


@api.get("/cancer-patients/terminology/{property}", response=List[CodedConceptSchema])
def get_cancer_patient_terminology(request, property: str):
    try:
        model_field = CancerPatient._meta.get_field(property)
        wrong_type = not isinstance(model_field, (SingleCodedConceptField, MultipleCodedConceptField))
    except FieldDoesNotExist:
        wrong_type = True
    if wrong_type:
        return api.create_response(request, {"message": "Invalid property"}, status=400)
    CodedConceptModel = model_field.remote_field.model
    return CodedConceptModel.objects.all()
