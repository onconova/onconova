from fhircraft.fhir.resources.datatypes.R4.complex import Reference, Narrative
from onconova.core.serialization.base import DjangoGetter
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import PrimaryCancerCondition as fhir
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept
from onconova.oncology.models.neoplastic_entity import (
    NeoplasticEntityRelationshipChoices,
)


class PrimaryCancerConditionProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaPrimaryCancerCondition
):

    __model__ = models.NeoplasticEntity
    __schema__ = schemas.NeoplasticEntity

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaPrimaryCancerCondition
    ) -> schemas.NeoplasticEntityCreate:
        return schemas.NeoplasticEntityCreate(
            externalSource=None,
            externalSourceId=None,
            relationship=(
                NeoplasticEntityRelationshipChoices.LOCAL_RECURRENCE
                if obj.fhirpath_single(
                    "Condition.clinicalStatus.coding.code = 'recurrence' and Condition.clinicalStatus.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-primary-cancer-recurrence-type').valueCodeableConcept.coding.code = '255470001'"
                )
                else (
                    NeoplasticEntityRelationshipChoices.REGIONAL_RECURRENCE
                    if obj.fhirpath_single(
                        "Condition.clinicalStatus.coding.code = 'recurrence' and Condition.clinicalStatus.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-primary-cancer-recurrence-type').valueCodeableConcept.coding.code = '410674003'"
                    )
                    else NeoplasticEntityRelationshipChoices.PRIMARY
                )
            ),
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
                "Condition.clinicalStatus.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-primary-cancer-recurrence-of').valueReference.reference.replace('Condition/', '')"
            ),
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
    ) -> fhir.OnconovaPrimaryCancerCondition:
        resource: fhir.OnconovaPrimaryCancerCondition = (
            fhir.OnconovaPrimaryCancerCondition.model_construct()
        )  # type: ignore
        resource.id = str(obj.id)
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.bodySite = fhir.OnconovaPrimaryCancerConditionBodySite(
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
        if obj.relationship == NeoplasticEntityRelationshipChoices.METASTATIC:
            raise ValueError(
                "NeoplasticEntity relationship cannot be 'metastatic' for PrimaryCancerCondition"
            )
        if (
            obj.relationship == NeoplasticEntityRelationshipChoices.LOCAL_RECURRENCE
            or obj.relationship
            == NeoplasticEntityRelationshipChoices.REGIONAL_RECURRENCE
        ):
            resource.clinicalStatus = fhir.OnconovaPrimaryCancerConditionClinicalStatus(
                coding=[
                    fhir.Coding(
                        code="recurrence",
                        system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                    )
                ],
                extension=[
                    fhir.PrimaryCancerRecurrenceType(
                        valueCodeableConcept=fhir.CodeableConcept(
                            coding=[
                                (
                                    fhir.Coding(
                                        code="255470001",
                                        display="Local",
                                        system="http://snomed.info/sct",
                                    )
                                    if obj.relationship
                                    == NeoplasticEntityRelationshipChoices.LOCAL_RECURRENCE
                                    else fhir.Coding(
                                        code="410674003",
                                        display="Regional",
                                        system="http://snomed.info/sct",
                                    )
                                )
                            ]
                        )
                    ),
                    fhir.PrimaryCancerRecurrenceOf(
                        valueReference=Reference(
                            reference=f"Condition/{obj.relatedPrimaryId}",
                        )
                    ),
                ],
            )
        return resource
