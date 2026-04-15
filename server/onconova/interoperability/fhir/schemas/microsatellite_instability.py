from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import MicrosatelliteInstability as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept


class MicrosatelliteInstabilityProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaMicrosatelliteInstability
):

    __model__ = models.MicrosatelliteInstability
    __schema__ = schemas.MicrosatelliteInstability

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaMicrosatelliteInstability
    ) -> schemas.MicrosatelliteInstabilityCreate:
        return schemas.MicrosatelliteInstabilityCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            value=CodedConcept.model_validate(
                obj.fhirpath_single(
                    "Observation.valueCodeableConcept.coding"
                ).model_dump()
            ),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.MicrosatelliteInstability
    ) -> fhir.OnconovaMicrosatelliteInstability:
        resource = fhir.OnconovaMicrosatelliteInstability.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.valueCodeableConcept = construct_fhir_codeable_concept(obj.value)
        return resource
