from fhircraft.fhir.resources.datatypes.R4.complex import (
    Narrative,
    Reference,
    Duration,
    Coding,
)
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
    MappingRule,
)
from onconova.interoperability.fhir.models import TherapyLine as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept
from onconova.oncology.models.therapy_line import TherapyLineIntentChoices


class TherapyLineProfile(OnconovaFhirBaseSchema, fhir.OnconovaTherapyLine):

    __model__ = models.TherapyLine
    __schema__ = schemas.TherapyLine

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaTherapyLine
    ) -> schemas.TherapyLineCreate:
        return schemas.TherapyLineCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single("EpisodeOfCare.patient.reference").replace(
                "Patient/", ""
            ),
            ordinal=obj.fhirpath_single(
                "EpisodeOfCare.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-therapy-line-number').valuePositiveInt"
            ),
            intent=cls.map_to_internal(
                "intent",
                obj.fhirpath_single(
                    "EpisodeOfCare.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-therapy-line-intent').valueCodeableConcept.coding"
                ),
            ),
            progressionDate=obj.fhirpath_single(
                "EpisodeOfCare.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-therapy-line-progression-date').valueDate"
            ),
        )

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.TherapyLine) -> fhir.OnconovaTherapyLine:
        resource = fhir.OnconovaTherapyLine.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.patient = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        if obj.period:
            resource.period = fhir.Period(
                start=(obj.period.start.isoformat() if obj.period.start else None),
                end=obj.period.end.isoformat() if obj.period.end else None,
            )
        resource.extension = [
            fhir.TherapyLineNumber(
                valuePositiveInt=obj.ordinal,
            ),
            fhir.TherapyLineIntent(
                valueCodeableConcept=construct_fhir_codeable_concept(
                    cls.map_to_fhir("intent", obj.intent)
                )
            ),
        ]
        if obj.progressionDate is not None:
            resource.extension.append(
                fhir.TherapyLineProgressionDate(
                    valueDate=obj.progressionDate.isoformat()
                )
            )
        if obj.progressionFreeSurvival is not None:
            resource.extension.append(
                fhir.TherapyLineProgressionFreeSurvival(
                    valueDuration=Duration(
                        value=obj.progressionFreeSurvival,
                        code="mo",
                        system="http://unitsofmeasure.org",
                    )
                )
            )
        return resource


TherapyLineProfile.register_mapping(
    "intent",
    [
        MappingRule(
            TherapyLineIntentChoices.CURATIVE,
            Coding(
                code="373808002",
                system="http://snomed.info/sct",
                display="Curative - procedure intent",
            ),
        ),
        MappingRule(
            TherapyLineIntentChoices.PALLIATIVE,
            Coding(
                code="363676003",
                system="http://snomed.info/sct",
                display="Palliative  - procedure intent",
            ),
        ),
    ],
)
