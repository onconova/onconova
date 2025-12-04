from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference, Quantity
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import TumorNeoantigenBurden as fhir
from onconova.oncology import models, schemas


class TumorNeoantigenBurdenProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaTumorNeoantigenBurden
):

    __model__ = models.TumorNeoantigenBurden
    __schema__ = schemas.TumorNeoantigenBurden

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaTumorNeoantigenBurden
    ) -> schemas.TumorNeoantigenBurdenCreate:
        return schemas.TumorNeoantigenBurdenCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single("Observation.subject.reference").replace(
                "Patient/", ""
            ),
            date=obj.fhirpath_single("Observation.effectiveDateTime"),
            value=obj.fhirpath_single("Observation.valueQuantity.value"),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.TumorNeoantigenBurden
    ) -> fhir.OnconovaTumorNeoantigenBurden:
        resource = fhir.OnconovaTumorNeoantigenBurden.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.valueQuantity = Quantity(
            value=obj.value,
            code="1/1000000{Neoantigen}",
            system="http://unitsofmeasure.org",
        )
        return resource
