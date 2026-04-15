from fhircraft.fhir.resources.datatypes.R4.complex import (
    Reference,
    Narrative,
)
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
)
from onconova.interoperability.fhir.models import CancerRiskAssessment as fhir
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept


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
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            assessedEntitiesIds=[
                ref.replace("Condition/", "")
                for ref in obj.fhirpath_values("Observation.focus.reference.getValue()")
            ],
            methodology=CodedConcept.model_validate(
                obj.fhirpath_single("Observation.code.coding").model_dump()
            ),
            risk=CodedConcept.model_validate(
                obj.fhirpath_single(
                    "Observation.valueCodeableConcept.coding"
                ).model_dump()
            ),
            score=obj.fhirpath_single(
                "Observation.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-risk-assessment-score').value.getValue()"
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
        resource.code = construct_fhir_codeable_concept(obj.methodology)
        resource.valueCodeableConcept = construct_fhir_codeable_concept(obj.risk)
        if obj.score:
            resource.extension = [
                fhir.RiskAssessmentScore(
                    valueDecimal=obj.score if isinstance(obj.score, float) else None,
                    valueInteger=obj.score if isinstance(obj.score, int) else None,
                )
            ]

        return resource
