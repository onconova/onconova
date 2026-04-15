from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference, Quantity
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import LossOfHeterozygosity as fhir
from onconova.oncology import models, schemas


class LossOfHeterozygosityProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaLossOfHeterozygosity
):

    __model__ = models.LossOfHeterozygosity
    __schema__ = schemas.LossOfHeterozygosity

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaLossOfHeterozygosity
    ) -> schemas.LossOfHeterozygosityCreate:
        return schemas.LossOfHeterozygosityCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            value=obj.fhirpath_single("Observation.valueQuantity.value.getValue()"),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.LossOfHeterozygosity
    ) -> fhir.OnconovaLossOfHeterozygosity:
        resource = fhir.OnconovaLossOfHeterozygosity.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.valueQuantity = fhir.OnconovaLossOfHeterozygosityValueQuantity(
            value=obj.value
        )
        return resource
