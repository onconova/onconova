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
from onconova.interoperability.fhir.models import (
    HomologousRecombinationDeficiency as fhir,
)
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.oncology.models.genomic_signature import (
    HomologousRecombinationDeficiencyInterpretationChoices,
)


class HomologousRecombinationDeficiencyProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaHomologousRecombinationDeficiency
):

    __model__ = models.HomologousRecombinationDeficiency
    __schema__ = schemas.HomologousRecombinationDeficiency

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaHomologousRecombinationDeficiency
    ) -> schemas.HomologousRecombinationDeficiencyCreate:
        return schemas.HomologousRecombinationDeficiencyCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Observation.subject.reference.getValue()"
            ).replace("Patient/", ""),
            date=obj.fhirpath_single("Observation.effectiveDateTime.getValue()"),
            value=obj.fhirpath_single("Observation.valueQuantity.value.getValue()"),
            interpretation=(
                cls.map_to_internal("interpretation", interpretation)
                if (
                    interpretation := obj.fhirpath_single(
                        "Observation.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-homologous-recombination-deficiency-interpretation').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
        )

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.HomologousRecombinationDeficiency
    ) -> fhir.OnconovaHomologousRecombinationDeficiency:
        resource = fhir.OnconovaHomologousRecombinationDeficiency.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.valueQuantity = (
            fhir.OnconovaHomologousRecombinationDeficiencyValueQuantity(value=obj.value)
        )
        resource.extension = [
            fhir.Extension(
                url="http://onconova.github.io/fhir/StructureDefinition/onconova-ext-homologous-recombination-deficiency-interpretation",
                valueCodeableConcept=construct_fhir_codeable_concept(
                    cls.map_to_fhir("interpretation", obj.interpretation)
                ),
            )
        ]
        return resource


HomologousRecombinationDeficiencyProfile.register_mapping(
    "interpretation",
    [
        MappingRule(
            HomologousRecombinationDeficiencyInterpretationChoices.POSITIVE,
            Coding(
                code="10828004",
                system="http://snomed.info/sct",
                display="Positive",
            ),
        ),
        MappingRule(
            HomologousRecombinationDeficiencyInterpretationChoices.NEGATIVE,
            Coding(
                code="260385009",
                system="http://snomed.info/sct",
                display="Negative",
            ),
        ),
        MappingRule(
            HomologousRecombinationDeficiencyInterpretationChoices.INDETERMINATE,
            Coding(
                code="82334004",
                system="http://snomed.info/sct",
                display="Indetermediate",
            ),
        ),
    ],
)
