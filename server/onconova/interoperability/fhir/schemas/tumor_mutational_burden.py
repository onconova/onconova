from fhircraft.fhir.resources.datatypes.R4.complex import (
    Narrative,
    Reference,
    Quantity,
    Coding,
)
from onconova.interoperability.fhir.schemas.base import (
    MappingRule,
    OnconovaFhirBaseSchema,
)
import re
from onconova.interoperability.fhir.models import TumorMutationalBurden as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept
from onconova.oncology.models.genomic_signature import (
    TumorMutationalBurdenStatusChoices,
)


class TumorMutationalBurdenProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaTumorMutationalBurden
):

    __model__ = models.TumorMutationalBurden
    __schema__ = schemas.TumorMutationalBurden

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaTumorMutationalBurden
    ) -> schemas.TumorMutationalBurdenCreate:
        return schemas.TumorMutationalBurdenCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            value=obj.fhirpath_single("Observation.valueQuantity.value.getValue()"),
            status=(
                cls.map_to_internal("statusInterpretation", status)
                if (
                    status := obj.fhirpath_single(
                        "Observation.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-vs-tumor-mutational-burden-status').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.TumorMutationalBurden
    ) -> fhir.OnconovaTumorMutationalBurden:
        resource = fhir.OnconovaTumorMutationalBurden.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.valueQuantity = Quantity(
            value=obj.value, code="1/1000000{Base}", system="http://unitsofmeasure.org"
        )
        resource.extension = [
            fhir.Extension(
                url="http://onconova.github.io/fhir/StructureDefinition/onconova-vs-tumor-mutational-burden-status",
                valueCodeableConcept=construct_fhir_codeable_concept(
                    cls.map_to_fhir("statusInterpretation", obj.status)
                ),
            )
        ]
        return resource


TumorMutationalBurdenProfile.register_mapping(
    "statusInterpretation",
    [
        MappingRule(
            TumorMutationalBurdenStatusChoices.LOW,
            Coding(
                code="L",
                system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                display="Low",
            ),
        ),
        MappingRule(
            TumorMutationalBurdenStatusChoices.INTERMEDIATE,
            Coding(
                code="I",
                system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                display="Intermediate",
            ),
        ),
        MappingRule(
            TumorMutationalBurdenStatusChoices.HIGH,
            Coding(
                code="H",
                system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                display="HIGH",
            ),
        ),
        MappingRule(
            TumorMutationalBurdenStatusChoices.INDETERMINATE,
            Coding(
                code="IND",
                system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                display="Indetermediate",
            ),
        ),
    ],
)
