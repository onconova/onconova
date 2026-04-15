from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import ECOGPerformanceStatus as fhir
from onconova.interoperability.fhir.models import KarnofskyPerformanceStatus as fhir_
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas


class ECOGPerformanceStatusProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaECOGPerformanceStatus
):

    __model__ = models.PerformanceStatus
    __schema__ = schemas.PerformanceStatus

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaECOGPerformanceStatus
    ) -> schemas.PerformanceStatusCreate:
        return schemas.PerformanceStatusCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            ecogScore=obj.fhirpath_single("Observation.valueInteger.getValue()"),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.PerformanceStatus
    ) -> fhir.OnconovaECOGPerformanceStatus:
        resource = fhir.OnconovaECOGPerformanceStatus.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.valueInteger = obj.ecogScore
        if obj.ecogInterpretation:
            resource.interpretation = [
                construct_fhir_codeable_concept(obj.ecogInterpretation)
            ]
        return resource


class KarnofskyPerformanceStatusProfile(
    OnconovaFhirBaseSchema, fhir_.OnconovaKarnofskyPerformanceStatus
):

    __model__ = models.PerformanceStatus
    __schema__ = schemas.PerformanceStatus

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir_.OnconovaKarnofskyPerformanceStatus
    ) -> schemas.PerformanceStatusCreate:
        return schemas.PerformanceStatusCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            karnofskyScore=obj.fhirpath_single("Observation.valueInteger.getValue()"),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.PerformanceStatus
    ) -> fhir_.OnconovaKarnofskyPerformanceStatus:
        resource = fhir_.OnconovaKarnofskyPerformanceStatus.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.valueInteger = obj.karnofskyScore
        if obj.karnofskyInterpretation:
            resource.interpretation = [
                construct_fhir_codeable_concept(obj.karnofskyInterpretation)
            ]
        return resource
