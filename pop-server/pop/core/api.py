from ninja import NinjaAPI, Redoc, Swagger
from pop.core.models import CancerPatient 

api = NinjaAPI(docs=Swagger())

@api.get("/hello")
def hello(request):
    return "Hello world"

from ninja import ModelSchema

class CancerPatientSchema(ModelSchema):
    class Meta:
        model = CancerPatient
        exclude = ['auto_id']
        depth=1


@api.get("/patch/{id}", response=CancerPatientSchema)
def get_cancer_patient_by_id(request, id: str):
    return CancerPatient.objects.get(id=id)