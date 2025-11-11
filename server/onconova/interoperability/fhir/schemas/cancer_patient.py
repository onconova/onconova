from onconova.interoperability.fhir import models as fhir_models
from onconova.oncology import schemas
from onconova.oncology import models

from ninja import Schema
from pydantic import model_validator

class OnconovaCancerPatient(fhir_models.OnconovaCancerPatient, Schema):

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.PatientCase) -> fhir_models.OnconovaCancerPatient:
        return fhir_models.OnconovaCancerPatient(**obj.dict())

    @model_validator(mode="before")
    @classmethod
    def pre_validator(cls, obj):
        print('VALIDATING:' , obj)
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, Schema):
            return cls.onconova_to_fhir(obj)        
        else:
            obj = schemas.PatientCase.model_validate(obj)
            return cls.onconova_to_fhir(obj)
    
