from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import TumorBoardReview as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.oncology.models.tumor_board import TumorBoardSpecialties
from onconova.core.schemas import CodedConcept
from pydantic import field_validator


class TumorBoardReviewProfile(OnconovaFhirBaseSchema, fhir.OnconovaTumorBoardReview):

    __model__ = models.UnspecifiedTumorBoard
    __schema__ = schemas.UnspecifiedTumorBoard

    @field_validator("code", mode="after", check_fields=False)
    @classmethod
    def discriminator(cls, concept: fhir.CodeableConcept) -> fhir.CodeableConcept:
        if not concept.fhirpath_single(
            "coding.code = 'C93304'"
        ) or concept.fhirpath_single(
            "extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-tumor-board-specialization').exists()"
        ):
            assert concept.coding
            raise ValueError(
                f"The code {concept.coding[0].system}#{concept.coding[0].code} is not a valid unspecified tumor board code discriminator"
            )
        return concept

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaTumorBoardReview
    ) -> schemas.UnspecifiedTumorBoardCreate:
        return schemas.UnspecifiedTumorBoardCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Procedure.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Procedure.performedDateTime.getValue()"),
            recommendations=[
                CodedConcept.model_validate(coding.model_dump())
                for coding in obj.fhirpath_values("Procedure.followUp.coding")
            ],
            relatedEntitiesIds=obj.fhirpath_values(
                "Procedure.reasonReference.reference.getValue().replace('Condition/','')"
            ),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.UnspecifiedTumorBoard
    ) -> fhir.OnconovaTumorBoardReview:

        if obj.category != TumorBoardSpecialties.UNSPECIFIED:
            raise ValueError(
                "Only unspecified tumor boards are supported by this profile"
            )

        resource = fhir.OnconovaTumorBoardReview.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.performedDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.reasonReference = [
            Reference(
                reference=f"Condition/{conditionId}",
            )
            for conditionId in obj.relatedEntitiesIds or []
        ]
        resource.followUp = [
            construct_fhir_codeable_concept(recommendation)
            for recommendation in obj.recommendations or []
        ]
        return resource
