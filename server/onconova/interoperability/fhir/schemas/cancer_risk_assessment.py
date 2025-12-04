from fhircraft.fhir.resources.datatypes.R4.complex import (
    Reference,
    Coding,
    CodeableConcept,
    Narrative,
)
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
)
from onconova.interoperability.fhir.models import CancerRiskAssessment as fhir
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept


class CancerRiskAssessmentProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaCancerRiskAssessment
):

    __model__ = models.RiskAssessment
    __schema__ = schemas.RiskAssessment

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaCancerRiskAssessment
    ) -> schemas.RiskAssessmentCreate:
        return schemas.RiskAssessmentCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single("Observation.subject.reference").replace(
                "Patient/", ""
            ),
            date=obj.fhirpath_single("Observation.effectiveDateTime"),
            assessedEntitiesIds=[
                ref.replace("Condition/", "")
                for ref in obj.fhirpath_values("Observation.focus.reference")
            ],
            methodology=CodedConcept.model_validate(
                obj.fhirpath_single("Observation.code.coding")
            ),
            risk=CodedConcept.model_validate(
                obj.fhirpath_single("Observation.valueCodeableConcept.coding")
            ),
            score=obj.fhirpath_single(
                "Observation.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-risk-assessment-score').value"
            ),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.RiskAssessment
    ) -> fhir.OnconovaCancerRiskAssessment:
        resource = fhir.OnconovaCancerRiskAssessment.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.focus = [
            Reference(reference=f"Condition/{cond_id}")
            for cond_id in obj.assessedEntitiesIds or []
        ]
        resource.code = CodeableConcept(
            coding=[Coding.model_validate(obj.methodology.model_dump())]
        )
        resource.valueCodeableConcept = CodeableConcept(
            coding=[Coding.model_validate(obj.risk.model_dump())]
        )
        if obj.score:
            resource.extension = [
                fhir.RiskAssessmentScore(
                    valueDecimal=obj.score if isinstance(obj.score, float) else None,
                    valueInteger=obj.score if isinstance(obj.score, int) else None,
                )
            ]

        return resource
