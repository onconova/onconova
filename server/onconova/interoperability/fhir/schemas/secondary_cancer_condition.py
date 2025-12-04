from fhircraft.fhir.resources.datatypes.R4.complex import Reference, Narrative
from onconova.core.schemas import CodedConcept
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import SecondaryCancerCondition as fhir
from onconova.oncology import models, schemas
from onconova.oncology.models.neoplastic_entity import (
    NeoplasticEntityRelationshipChoices,
)


class SecondaryCancerConditionProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaSecondaryCancerCondition
):

    __model__ = models.NeoplasticEntity
    __schema__ = schemas.NeoplasticEntity

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaSecondaryCancerCondition
    ) -> schemas.NeoplasticEntityCreate:
        return schemas.NeoplasticEntityCreate(
            externalSource=None,
            externalSourceId=None,
            relationship=NeoplasticEntityRelationshipChoices.METASTATIC,
            caseId=obj.fhirpath_single("Condition.subject.reference").replace(
                "Patient/", ""
            ),
            topography=obj.fhirpath_single("Condition.bodySite.coding"),
            differentitation=(
                CodedConcept.model_validate(
                    obj.fhirpath_single(
                        "Condition.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-histological-differentiation').valueCodeableConcept.coding"
                    )
                )
            ),
            relatedPrimaryId=obj.fhirpath_single(
                "Condition.extension('http://hl7.org/fhir/StructureDefinition/condition-related').valueReference.reference"
            ).replace("Condition/", ""),
            laterality=(
                CodedConcept.model_validate(coding)
                if (
                    coding := obj.fhirpath_single(
                        "Condition.bodySite.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-laterality-qualifier').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            morphology=(
                CodedConcept.model_validate(
                    obj.fhirpath_single(
                        "Condition.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-histology-morphology-behavior').valueCodeableConcept.coding"
                    )
                )
            ),
            assertionDate=obj.fhirpath_single(
                "Condition.extension('http://hl7.org/fhir/StructureDefinition/condition-assertedDate').valueDateTime"
            ),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.NeoplasticEntity
    ) -> fhir.OnconovaSecondaryCancerCondition:
        if obj.relationship != NeoplasticEntityRelationshipChoices.METASTATIC:
            raise ValueError(
                "NeoplasticEntity relationship must be 'metastatic' for SecondaryCancerCondition"
            )
        resource: fhir.OnconovaSecondaryCancerCondition = (
            fhir.OnconovaSecondaryCancerCondition.model_construct()
        )
        resource.id = str(obj.id)
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.bodySite = fhir.OnconovaSecondaryCancerConditionBodySite(
            coding=[fhir.Coding.model_validate(obj.topography.model_dump())],
            extension=(
                [
                    fhir.LateralityQualifier(
                        valueCodeableConcept=fhir.CodeableConcept(
                            coding=[
                                fhir.Coding.model_validate(obj.laterality.model_dump())
                            ]
                        )
                    )
                ]
                if obj.laterality
                else None
            ),
        )
        resource.extension = [
            fhir.HistologyMorphologyBehavior(
                valueCodeableConcept=fhir.CodeableConcept(
                    coding=[fhir.Coding.model_validate(obj.morphology.model_dump())]
                )
            ),
            fhir.ConditionAssertedDate(valueDateTime=obj.assertionDate.isoformat()),
        ]
        if obj.differentitation:
            resource.extension.append(
                fhir.HistologicalDifferentiation(
                    valueCodeableConcept=fhir.CodeableConcept(
                        coding=[
                            fhir.Coding.model_validate(
                                obj.differentitation.model_dump()
                            )
                        ]
                    )
                )
            )
        assert resource.extension is not None
        if obj.relatedPrimaryId:
            resource.extension.append(
                fhir.ConditionRelated(
                    valueReference=Reference(
                        reference=f"Condition/{obj.relatedPrimaryId}",
                    )
                )
            )

        return resource
