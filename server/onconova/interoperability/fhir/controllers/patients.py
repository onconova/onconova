from ninja_extra import ControllerBase, api_controller, route
from django.shortcuts import get_object_or_404

from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.oncology.models import (
    PatientCase,
)
from onconova.interoperability.fhir.models.CancerPatient import (
    OnconovaIdentifier, CancerPatient, USCoreRaceExtension, DataCompletionRate, Narrative, AgeExtension, Range, AgeAtDiagnosis, Quantity
)
from onconova.oncology import schemas
from onconova.oncology import models



def convert_from_onconova(orm_instance: models.PatientCase):
    
    obj: schemas.PatientCaseSchema = schemas.PatientCaseSchema.model_validate(orm_instance)
    return CancerPatient.model_validate(dict(
        id=str(obj.id),
        text=Narrative(div=f"<div xmlns=\"http://www.w3.org/1999/xhtml\">{obj.description}</div>"),
        identifier=[
            OnconovaIdentifier(value=obj.pseudoidentifier)
        ],
        birthDate=obj.dateOfBirth,
        gender=obj.gender.code,
        deceasedDateTime=obj.dateOfDeath if obj.dateOfDeath else None,
        extension=list(filter(None,[
            USCoreRaceExtension(valueCodeableConcept=obj.race) if obj.race else None,
            DataCompletionRate(valueDecimal=obj.dataCompletionRate) if obj.dataCompletionRate != None else None, 
        ]))            
    ))


@api_controller(
    "Patient/{id}",
    auth=None,
    tags=["Patients"],
)
class PatientController(ControllerBase):

    @route.get(
        path="",
        response={200: CancerPatient, **COMMON_HTTP_ERRORS},
        permissions=None,
        operation_id="readPatient",
        exclude_none=True,
    )
    def read_patient(self, id: str): 
        return convert_from_onconova(
            get_object_or_404(PatientCase, id=id)
        )
