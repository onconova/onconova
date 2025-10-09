from onconova.interoperability.fhir import models as fhir_models
from onconova.oncology import schemas
from onconova.oncology import models

from ninja import Schema
from pydantic import model_validator

class CancerPatient(fhir_models.CancerPatient, Schema):

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.PatientCase) -> fhir_models.CancerPatient:
        return fhir_models.CancerPatient(**obj.dict())

    @model_validator(mode="before")
    def validator(cls, obj):
        if isinstance(obj, schemas.PatientCase):
            return cls.onconova_to_fhir(obj)
        
        elif isinstance(obj, models.PatientCase):
            return cls.validator(schemas.PatientCase.model_validate(obj))
        
        return obj
    

