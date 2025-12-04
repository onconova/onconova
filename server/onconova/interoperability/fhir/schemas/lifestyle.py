from fhircraft.fhir.resources.datatypes.R4.complex import (
    Narrative,
    Reference,
    Quantity,
    Coding,
)
from onconova.interoperability.fhir.schemas.base import (
    MappingRule,
    OnconovaFhirBaseSchema,
)
import re
from onconova.interoperability.fhir.models import Lifestyle as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept, Measure

# from onconova.oncology.models.lifestyle import Cho


class LifestyleProfile(OnconovaFhirBaseSchema, fhir.OnconovaLifestyle):

    __model__ = models.Lifestyle
    __schema__ = schemas.Lifestyle

    @classmethod
    def fhir_to_onconova(cls, obj: fhir.OnconovaLifestyle) -> schemas.LifestyleCreate:
        return schemas.LifestyleCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single("Observation.subject.reference").replace(
                "Patient/", ""
            ),
            date=obj.fhirpath_single("Observation.effectiveDateTime"),
            smokingStatus=(
                CodedConcept.model_validate(coding)
                if (
                    coding := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='72166-2').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            smokingPackyears=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='8664-5').valueQuantity.value"
            ),
            smokingQuited=(
                Measure(value=quantity.value, unit=quantity.code)
                if (
                    quantity := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='107339-4').valueQuantity"
                    )
                )
                else None
            ),
            alcoholConsumption=(
                CodedConcept.model_validate(coding)
                if (
                    coding := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='1106630-7').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            recreationalDrugs=(
                [CodedConcept.model_validate(drug) for drug in drugs]
                if (
                    drugs := obj.fhirpath_values(
                        "Observation.component.where(code.coding.code='C84368').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            exposures=(
                [CodedConcept.model_validate(exposure) for exposure in exposures]
                if (
                    exposures := obj.fhirpath_values(
                        "Observation.component.where(code.coding.code='C16552').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            nightSleep=(
                Measure(value=quantity.value, unit=quantity.code)
                if (
                    quantity := obj.fhirpath_single(
                        "Observation.component.where(code.coding.code='93832-4').valueQuantity"
                    )
                )
                else None
            ),
        )

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.Lifestyle) -> fhir.OnconovaLifestyle:
        resource = fhir.OnconovaLifestyle.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.component = resource.component or []
        if obj.smokingStatus:
            resource.component.append(
                fhir.OnconovaLifestyleSmokingStatus(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        obj.smokingStatus
                    )
                )
            )
        if obj.smokingPackyears is not None:
            resource.component.append(
                fhir.OnconovaLifestyleSmokingPackyears(
                    valueQuantity=Quantity(
                        value=obj.smokingPackyears,
                        code="{pack-year}",
                        system="http://unitsofmeasure.org",
                    )
                )
            )
        if obj.smokingQuited is not None:
            resource.component.append(
                fhir.OnconovaLifestyleSmokingQuited(
                    valueQuantity=Quantity(
                        value=obj.smokingQuited.value,
                        code=obj.smokingQuited.unit,
                        system="http://unitsofmeasure.org",
                    )
                )
            )
        if obj.alcoholConsumption:
            resource.component.append(
                fhir.OnconovaLifestyleAlcoholConsumption(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        obj.alcoholConsumption
                    )
                )
            )
        if obj.nightSleep is not None:
            resource.component.append(
                fhir.OnconovaLifestyleNightSleep(
                    valueQuantity=Quantity(
                        value=obj.nightSleep.value,
                        code=obj.nightSleep.unit,
                        system="http://unitsofmeasure.org",
                    )
                )
            )
        for drug in obj.recreationalDrugs or []:
            resource.component.append(
                fhir.OnconovaLifestyleRecreationalDrug(
                    valueCodeableConcept=construct_fhir_codeable_concept(drug)
                )
            )
        for exposure in obj.exposures or []:
            resource.component.append(
                fhir.OnconovaLifestyleExposures(
                    valueCodeableConcept=construct_fhir_codeable_concept(exposure)
                )
            )
        return resource
