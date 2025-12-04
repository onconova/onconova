from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import CancerFamilyMemberHistory as fhir
from onconova.interoperability.fhir.models import KarnofskyPerformanceStatus as fhir_
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept


class CancerFamilyMemberHistoryProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaCancerFamilyMemberHistory
):

    __model__ = models.FamilyHistory
    __schema__ = schemas.FamilyHistory

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaCancerFamilyMemberHistory
    ) -> schemas.FamilyHistoryCreate:
        condition: fhir.OnconovaCancerFamilyMemberHistoryCancerCondition | None = (
            obj.fhirpath_single(
                "FamilyMemberHistory.condition.where(code.coding.code='363346000')"
            )
        )
        return schemas.FamilyHistoryCreate(
            caseId=obj.fhirpath_single("FamilyMemberHistory.patient.reference").replace(
                "Patient/", ""
            ),
            date=obj.fhirpath_single("FamilyMemberHistory.date"),
            isDeceased=obj.fhirpath_single("FamilyMemberHistory.deceasedBoolean"),
            relationship=CodedConcept.model_validate(
                obj.fhirpath_single("FamilyMemberHistory.relationship.coding")
            ),
            hadCancer=condition is not None,
            onsetAge=condition.fhirpath_single("onsetAge.value") if condition else None,
            contributedToDeath=(
                condition.fhirpath_single(
                    "extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-family-member-condition-contributed-to-death').valueBoolean"
                )
                if condition
                else None
            ),
            morphology=(
                CodedConcept.model_validate(coding)
                if condition
                and (
                    coding := condition.fhirpath_single(
                        "extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-family-history-member-cancer-morphology').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            topography=(
                CodedConcept.model_validate(coding)
                if condition
                and (
                    coding := condition.fhirpath_single(
                        "extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-family-history-member-cancer-topography').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.FamilyHistory
    ) -> fhir.OnconovaCancerFamilyMemberHistory:
        resource = fhir.OnconovaCancerFamilyMemberHistory.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.date = obj.date.isoformat()
        resource.patient = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.deceasedBoolean = obj.isDeceased

        resource.relationship = construct_fhir_codeable_concept(obj.relationship)
        if obj.hadCancer:
            condition = fhir.OnconovaCancerFamilyMemberHistoryCancerCondition(
                onsetAge=(
                    fhir.Age(
                        value=obj.onsetAge, system="http://unitsofmeasure.org", code="a"
                    )
                    if obj.onsetAge is not None
                    else None
                )
            )
            condition.extension = []
            if obj.contributedToDeath is not None:
                condition.extension.append(
                    fhir.FamilyMemberConditionContributedToDeath(
                        valueBoolean=obj.contributedToDeath
                    )
                )
            if obj.topography:
                condition.extension.append(
                    fhir.FamilyMemberHistoryCancerTopography(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            obj.topography
                        )
                    )
                )
            if obj.morphology:
                condition.extension.append(
                    fhir.FamilyMemberHistoryCancerMorphology(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            obj.morphology
                        )
                    )
                )
            resource.condition = [condition]

        return resource
