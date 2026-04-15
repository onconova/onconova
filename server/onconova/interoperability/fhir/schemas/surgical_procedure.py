from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference, Coding
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
    MappingRule,
)
from onconova.interoperability.fhir.models import SurgicalProcedure as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.oncology.models.surgery import SurgeryIntentChoices
from onconova.core.schemas import CodedConcept


class SurgicalProcedureProfile(OnconovaFhirBaseSchema, fhir.OnconovaSurgicalProcedure):

    __model__ = models.Surgery
    __schema__ = schemas.Surgery

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaSurgicalProcedure
    ) -> schemas.SurgeryCreate:
        return schemas.SurgeryCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Procedure.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Procedure.performedDateTime.getValue()"),
            procedure=CodedConcept.model_validate(
                obj.fhirpath_single("Procedure.code.coding").model_dump()
            ),
            intent=cls.map_to_internal(
                "TreatmentIntents",
                obj.fhirpath_single(
                    "Procedure.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-procedure-intent').valueCodeableConcept.coding"
                ),
            ),
            bodysite=(
                CodedConcept.model_validate(coding.model_dump())
                if (coding := obj.fhirpath_single("Procedure.bodySite.coding"))
                else None
            ),
            outcome=(
                CodedConcept.model_validate(coding.model_dump())
                if (coding := obj.fhirpath_single("Procedure.outcome.coding"))
                else None
            ),
            bodysiteQualifier=(
                CodedConcept.model_validate(coding.model_dump())
                if (
                    coding := obj.fhirpath_single(
                        "Procedure.bodySite.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-body-location-qualifier').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            bodysiteLaterality=(
                CodedConcept.model_validate(coding.model_dump())
                if (
                    coding := obj.fhirpath_single(
                        "Procedure.bodySite.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-laterality-qualifier').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            targetedEntitiesIds=obj.fhirpath_values(
                "Procedure.reasonReference.reference.replace('Condition/','')"
            ),
            therapyLineId=obj.fhirpath_single(
                "Procedure.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-therapy-line-reference').valueReference.reference.replace('List/','')"
            ),
        )

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.Surgery) -> fhir.OnconovaSurgicalProcedure:
        resource = fhir.OnconovaSurgicalProcedure.model_construct()
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
            for conditionId in obj.targetedEntitiesIds or []
        ]
        resource.code = construct_fhir_codeable_concept(obj.procedure)
        resource.extension = [
            fhir.ProcedureIntent(
                valueCodeableConcept=construct_fhir_codeable_concept(
                    cls.map_to_fhir("TreatmentIntents", obj.intent)
                )
            )
        ]
        if obj.therapyLineId:
            resource.extension.append(
                fhir.TherapyLineReference(
                    valueReference=Reference(reference=f"List/{obj.therapyLineId}")
                )
            )
        if obj.bodysite:
            resource.bodySite = [
                fhir.CancerRelatedSurgicalProcedureBodySite(
                    **construct_fhir_codeable_concept(obj.bodysite).model_dump(),
                    extension=[
                        ext
                        for ext in [
                            (
                                fhir.BodyLocationQualifier(
                                    valueCodeableConcept=construct_fhir_codeable_concept(
                                        obj.bodysiteQualifier
                                    )
                                )
                                if obj.bodysiteQualifier
                                else None
                            ),
                            (
                                fhir.LateralityQualifier(
                                    valueCodeableConcept=construct_fhir_codeable_concept(
                                        obj.bodysiteLaterality
                                    )
                                )
                                if obj.bodysiteLaterality
                                else None
                            ),
                        ]
                        if ext is not None
                    ],
                )
            ]
        if obj.outcome:
            resource.outcome = construct_fhir_codeable_concept(obj.outcome)
        return resource


SurgicalProcedureProfile.register_mapping(
    "TreatmentIntents",
    [
        MappingRule(
            SurgeryIntentChoices.CURATIVE,
            Coding(
                code="373808002",
                system="http://snomed.info/sct",
                display="Curative - procedure intent",
            ),
        ),
        MappingRule(
            SurgeryIntentChoices.PALLIATIVE,
            Coding(
                code="363676003",
                system="http://snomed.info/sct",
                display="Palliative  - procedure intent",
            ),
        ),
    ],
)
