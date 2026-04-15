from pydantic import field_validator
from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Reference, Coding
from fhircraft.fhir.resources.datatypes.R4.core import Observation
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
    MappingRule,
)
from onconova.interoperability.fhir.models import LymphomaStage as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept


class LymphomaStageProfile(OnconovaFhirBaseSchema, fhir.OnconovaLymphomaStage):

    __model__ = models.LymphomaStaging
    __schema__ = schemas.LymphomaStaging

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaLymphomaStage
    ) -> schemas.LymphomaStagingCreate:
        instance = schemas.LymphomaStagingCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue().replace('Patient/', '')"
            ),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            methodology=CodedConcept.model_validate(
                obj.fhirpath_single("Observation.method.coding").model_dump()
            ),
            stagedEntitiesIds=obj.fhirpath_values(
                "Observation.focus.reference.getValue().replace('Condition/', '')"
            ),
            stage=CodedConcept.model_validate(
                obj.fhirpath_single(
                    "Observation.valueCodeableConcept.coding"
                ).model_dump()
            ),
            bulky=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='260873006').valueCodeableConcept.coding.code='52101004'"
            ),
            pathological=obj.fhirpath_single(
                "Observation.component.where(code.coding.code='277366005').valueCodeableConcept.coding.code='261023001'"
            ),
            modifiers=[
                CodedConcept.model_validate(concept.model_dump())
                for concept in obj.fhirpath_values(
                    "Observation.component.where(code.coding.code='106252000').valueCodeableConcept.coding"
                )
            ],
        )
        return instance

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.LymphomaStaging
    ) -> fhir.OnconovaLymphomaStage:
        resource = fhir.OnconovaLymphomaStage.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.valueCodeableConcept = construct_fhir_codeable_concept(obj.stage)
        if obj.stagedEntitiesIds:
            resource.focus = [
                Reference(
                    reference=f"Condition/{entityId}",
                )
                for entityId in obj.stagedEntitiesIds
            ]
        if obj.methodology:
            resource.method = construct_fhir_codeable_concept(obj.methodology)

        if obj.bulky is not None:
            resource.component = resource.component or []
            resource.component.append(
                fhir.LymphomaStageBulkyModifier(
                    valueCodeableConcept=(
                        construct_fhir_codeable_concept(
                            Coding(
                                code="52101004",
                                system="http://snomed.info/sct",
                                display="Present (qualifier value)",
                            )
                        )
                        if obj.bulky
                        else construct_fhir_codeable_concept(
                            Coding(
                                code="2667000",
                                system="http://snomed.info/sct",
                                display="Absent (qualifier value)",
                            )
                        )
                    )
                )
            )
        if obj.pathological is not None:
            resource.component = resource.component or []
            resource.component.append(
                fhir.LymphomaStageClinOrPathModifier(
                    valueCodeableConcept=(
                        construct_fhir_codeable_concept(
                            Coding(
                                code="261023001",
                                system="http://snomed.info/sct",
                                display="Pathological staging (qualifier value)",
                            )
                        )
                        if obj.pathological
                        else construct_fhir_codeable_concept(
                            Coding(
                                code="260998006",
                                system="http://snomed.info/sct",
                                display="Clinical staging (qualifier value)",
                            )
                        )
                    )
                )
            )
        for modifier in obj.modifiers or []:
            resource.component = resource.component or []
            resource.component.append(
                fhir.LymphomaStageStageModifier(
                    valueCodeableConcept=(construct_fhir_codeable_concept(modifier))
                )
            )

        return resource
