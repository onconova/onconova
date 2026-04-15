from fhircraft.fhir.resources.datatypes.R4.complex import (
    Narrative,
    Reference,
    Quantity,
    Coding,
)
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
    MappingRule,
)
from onconova.interoperability.fhir.models import Comorbidities as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept
from onconova.oncology.models.comorbidities import ComorbiditiesAssessmentPanelChoices


class ComorbiditiesProfile(OnconovaFhirBaseSchema, fhir.OnconovaComorbidities):

    __model__ = models.ComorbiditiesAssessment
    __schema__ = schemas.ComorbiditiesAssessment

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaComorbidities
    ) -> schemas.ComorbiditiesAssessmentCreate:
        return schemas.ComorbiditiesAssessmentCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            indexConditionId=obj.fhirpath_single(
                "Observation.focus.reference.getValue()"
            ).replace("Condition/", ""),
            panel=(
                cls.map_to_internal("panel", panel)
                if (panel := obj.fhirpath_single("Observation.method.coding"))
                else None
            ),
            presentConditions=(
                [
                    CodedConcept.model_validate(condition.model_dump())
                    for condition in conditions
                ]
                if (
                    conditions := obj.fhirpath_values(
                        "Observation.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-related-condition').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            absentConditions=(
                [
                    CodedConcept.model_validate(condition.model_dump())
                    for condition in conditions
                ]
                if (
                    conditions := obj.fhirpath_values(
                        "Observation.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-related-condition-absent').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.ComorbiditiesAssessment
    ) -> fhir.OnconovaComorbidities:
        resource = fhir.OnconovaComorbidities.model_construct()
        resource.extension = resource.extension or []
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.focus = [
            Reference(
                reference=f"Condition/{obj.indexConditionId}",
            )
        ]
        if obj.panel:
            resource.method = construct_fhir_codeable_concept(
                cls.map_to_fhir("panel", obj.panel)
            )
        if obj.score is not None:
            resource.valueQuantity = fhir.OnconovaComorbiditiesValueQuantity(
                value=obj.score, code="1", system="http://unitsofmeasure.org"
            )
        for condition in obj.presentConditions or []:
            resource.extension.append(
                fhir.RelatedCondition(
                    valueCodeableConcept=construct_fhir_codeable_concept(condition)
                )
            )
        for condition in obj.absentConditions or []:
            resource.extension.append(
                fhir.RelatedConditionAbsent(
                    valueCodeableConcept=construct_fhir_codeable_concept(condition)
                )
            )
        return resource


ComorbiditiesProfile.register_mapping(
    "panel",
    [
        MappingRule(
            ComorbiditiesAssessmentPanelChoices.CHARLSON,
            Coding(
                code="charlson",
                system="http://onconova.github.io/fhir/CodeSystem/onconova-cs-comorbidity-panels",
                display="Charlson Comorbidity Panel",
            ),
        ),
        MappingRule(
            ComorbiditiesAssessmentPanelChoices.ELIXHAUSER,
            Coding(
                code="elixhauser",
                system="http://onconova.github.io/fhir/CodeSystem/onconova-cs-comorbidity-panels",
                display="Elixhauser Comorbidity Panel",
            ),
        ),
        MappingRule(
            ComorbiditiesAssessmentPanelChoices.NCI,
            Coding(
                code="nci",
                system="http://onconova.github.io/fhir/CodeSystem/onconova-cs-comorbidity-panels",
                display="NCI Comorbidity Panel",
            ),
        ),
    ],
)
