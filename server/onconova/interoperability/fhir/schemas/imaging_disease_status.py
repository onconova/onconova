from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference, Quantity
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import ImagingDiseaseStatus as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept


class ImagingDiseaseStatusProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaImagingDiseaseStatus
):

    __model__ = models.TreatmentResponse
    __schema__ = schemas.TreatmentResponse

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaImagingDiseaseStatus
    ) -> schemas.TreatmentResponseCreate:
        return schemas.TreatmentResponseCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue().replace('Patient/', '')"
            ),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            methodology=CodedConcept.model_validate(
                obj.fhirpath_single("Observation.method.coding").model_dump()
            ),
            recist=CodedConcept.model_validate(
                obj.fhirpath_single(
                    "Observation.valueCodeableConcept.coding"
                ).model_dump()
            ),
            recistInterpreted=obj.fhirpath_single(
                "Observation.valueCodeableConcept.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-treatment-response-recist-is-interpreted').valueBoolean.getValue()"
            ),
            assessedEntitiesIds=obj.fhirpath_values(
                "Observation.focus.reference.getValue().replace('Condition/', '')"
            ),
            assessedBodysites=(
                [
                    CodedConcept.model_validate(bodysite.model_dump())
                    for bodysite in bodysites
                ]
                if (bodysites := obj.fhirpath_values("Observation.bodySite.coding"))
                else None
            ),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.TreatmentResponse
    ) -> fhir.OnconovaImagingDiseaseStatus:
        resource = fhir.OnconovaImagingDiseaseStatus.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.method = construct_fhir_codeable_concept(obj.methodology)
        resource.valueCodeableConcept = (
            fhir.OnconovaImagingDiseaseStatusValueCodeableConcept(
                **construct_fhir_codeable_concept(obj.recist).model_dump()
            )
        )

        resource.bodySite = (
            construct_fhir_codeable_concept(obj.assessedBodysites[0])
            if obj.assessedBodysites
            else None
        )
        resource.focus = (
            [
                Reference(
                    reference=f"Condition/{conditionId}",
                )
                for conditionId in obj.assessedEntitiesIds
            ]
            if obj.assessedEntitiesIds
            else None
        )

        if obj.recistInterpreted is not None:
            resource.valueCodeableConcept.extension = [
                fhir.TreatmentResponseRecistIsInterpreted(
                    valueBoolean=obj.recistInterpreted,
                )
            ]

        return resource
