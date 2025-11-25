from fhircraft.fhir.resources.datatypes.R4.complex import Reference
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import TumorBoardReview as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept

class TumorBoardReviewProfile(OnconovaFhirBaseSchema, fhir.OnconovaTumorBoardReview):

    __model__ = models.UnspecifiedTumorBoard
    __schema__ = schemas.UnspecifiedTumorBoard

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaTumorBoardReview
    ) -> schemas.UnspecifiedTumorBoardCreate:
        return schemas.UnspecifiedTumorBoardCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single("Procedure.subject.reference").replace(
                "Patient/", ""
            ),
            date=obj.fhirpath_single("Procedure.performedDateTime"),
            recommendations=[CodedConcept.model_validate(coding) for coding in obj.fhirpath_values("Procedure.followUp.coding")],
            relatedEntitiesIds=obj.fhirpath_values("Procedure.reasonReference.reference.replace('Condition/','')"),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.UnspecifiedTumorBoard
    ) -> fhir.OnconovaTumorBoardReview:
        resource = fhir.OnconovaTumorBoardReview.model_construct()
        resource.id = str(obj.id)
        resource.text = fhir.Narrative(
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
            construct_fhir_codeable_concept(recommendation) for recommendation in obj.recommendations or []
        ]
        return resource