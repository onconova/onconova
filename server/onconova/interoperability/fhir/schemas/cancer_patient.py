from onconova.interoperability.fhir import models as fhir_models
from onconova.interoperability.fhir.models.CancerPatient import OnconovaIdentifier, AgeExtension, USCoreRaceExtension, DataCompletionRate, Narrative
from onconova.oncology import schemas
from onconova.oncology import models
from typing import Any
from ninja import Schema
from pydantic import model_validator
from pydantic import ConfigDict


class CancerPatient(fhir_models.CancerPatient):
    model_config = ConfigDict(from_attributes=False)

    @classmethod
    def convert_from_onconova(cls, obj: schemas.PatientCaseSchema):
        return cls(
            id=str(obj.id),
            text=Narrative(div=f"<div xmlns=\"http://www.w3.org/1999/xhtml\">{obj.description}</div>"),
            identifier=[
                OnconovaIdentifier(value=obj.pseudoidentifier)
            ],
            gender=obj.gender.code,
            birthDate=str(obj.dateOfBirth) if obj.dateOfBirth else None,
            deceasedDateTime=str(obj.dateOfDeath) if obj.dateOfDeath else None,
            extension=list(filter(None,[
                USCoreRaceExtension(valueCodeableConcept=obj.race) if obj.race else None,
                DataCompletionRate(valueDecimal=obj.dataCompletionRate) if obj.dataCompletionRate != None else None, 
            ]))            
        )

    @classmethod
    def model_validate(cls, obj: Any):
        if isinstance(obj, schemas.PatientCaseSchema):
            return cls.convert_from_onconova(obj)
        
        elif isinstance(obj, models.PatientCase):
            return cls.convert_from_onconova(schemas.PatientCaseSchema.model_validate(obj))
        
        return super().model_validate(obj)
    

