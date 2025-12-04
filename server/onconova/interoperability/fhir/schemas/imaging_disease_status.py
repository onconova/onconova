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
                "Observation.subject.reference.replace('Patient/', '')"
            ),
            date=obj.fhirpath_single("Observation.effectiveDateTime"),
            methodology=CodedConcept.model_validate(
                obj.fhirpath_single("Observation.method.coding")
            ),
            recist=CodedConcept.model_validate(
                obj.fhirpath_single("Observation.valueCodeableConcept.coding")
            ),
            recistInterpreted=obj.fhirpath_single(
                "Observation.valueCodeableConcept.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-treatment-response-recist-is-interpreted').valueBoolean"
            ),
            assessedEntitiesIds=obj.fhirpath_values(
                "Observation.focus.reference.replace('Condition/', '')"
            ),
            assessedBodysites=(
                [CodedConcept.model_validate(bodysite) for bodysite in bodysites]
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
        resource.valueCodeableConcept = construct_fhir_codeable_concept(obj.recist)

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
                fhir.Extension(
                    url="http://onconova.github.io/fhir/StructureDefinition/onconova-ext-treatment-response-recist-is-interpreted",
                    valueBoolean=obj.recistInterpreted,
                )
            ]

        return resource
