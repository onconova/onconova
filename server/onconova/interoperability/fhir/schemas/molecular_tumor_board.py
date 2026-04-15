from fhircraft.fhir.resources.datatypes.R4.complex import (
    Narrative,
    Reference,
    Narrative,
    Coding,
)
from django.shortcuts import get_object_or_404
from pydantic import field_validator
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema
from onconova.interoperability.fhir.models import MolecularTumorBoardReview as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.oncology.models.tumor_board import TumorBoardSpecialties
from onconova.core.schemas import CodedConcept


class MolecularTumorBoardReviewProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaMolecularTumorBoardReview
):

    __model__ = models.MolecularTumorBoard
    __schema__ = schemas.MolecularTumorBoard

    @field_validator("code", mode="after")
    @classmethod
    def discriminator(cls, concept: fhir.CodeableConcept) -> fhir.CodeableConcept:
        if not concept.fhirpath_single(
            "coding.code = 'C93304'"
        ) or not concept.fhirpath_single(
            "extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-tumor-board-specialization').valueCodeableConcept.coding.code = 'C20826'"
        ):
            raise ValueError(
                f"The code {concept.coding[0].system}#{concept.coding[0].code} is not a valid molecular tumor board code discriminator"
            )
        return concept

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaMolecularTumorBoardReview
    ) -> schemas.MolecularTumorBoardCreate:
        return schemas.MolecularTumorBoardCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Procedure.subject.reference.replace('Patient/', '')"
            ),
            date=obj.fhirpath_single("Procedure.performedDateTime.getValue()"),
            recommendations=[
                CodedConcept.model_validate(coding.model_dump())
                for coding in obj.fhirpath_values("Procedure.followUp.coding")
            ],
            relatedEntitiesIds=obj.fhirpath_values(
                "Procedure.reasonReference.reference.replace('Condition/','')"
            ),
            conductedMolecularComparison=obj.fhirpath_single(
                "Procedure.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-molecular-tumor-board-molecular-comparison').extension('conducted').valueBoolean.getValue()"
            ),
            molecularComparisonMatchId=obj.fhirpath_single(
                "Procedure.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-molecular-tumor-board-molecular-comparison').extension('matchedReference').valueReference.reference.getValue().replace('Condition/','')"
            ),
            conductedCupCharacterization=obj.fhirpath_single(
                "Procedure.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-molecular-tumor-board-cup-characterization').extension('conducted').valueBoolean.getValue()"
            ),
            characterizedCup=obj.fhirpath_single(
                "Procedure.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-molecular-tumor-board-cup-characterization').extension('success').valueBoolean.getValue()"
            ),
        )

    @classmethod
    def fhir_to_onconova_related(
        cls, obj: fhir.OnconovaMolecularTumorBoardReview
    ) -> list[
        tuple[
            models.MolecularTherapeuticRecommendation,
            schemas.MolecularTherapeuticRecommendation,
        ]
    ]:
        data = []
        recommendations: list[fhir.MolecularTumorBoardTherapeuticRecommendation] = (
            obj.fhirpath_values(
                "Procedure.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-molecular-tumor-board-therapeutic-recommendation')"
            )
        )
        for rec in recommendations:
            payload = schemas.MolecularTherapeuticRecommendation(
                clinicalTrial=rec.fhirpath_single(
                    "extension('clinicalTrial').valueString.getValue()"
                ),
                expectedEffect=(
                    CodedConcept.model_validate(coding.model_dump())
                    if (
                        coding := rec.fhirpath_single(
                            "extension('expectedEffect').valueCodeableConcept.coding"
                        )
                    )
                    else None
                ),
                offLabelUse=rec.fhirpath_single(
                    "extension('offLabelUse').valueBoolean.getValue()"
                ),
                withinSoc=rec.fhirpath_single(
                    "extension('withinSoc').valueBoolean.getValue()"
                ),
                drugs=[
                    CodedConcept.model_validate(drug.model_dump())
                    for drug in rec.fhirpath_values(
                        "extension('medication').valueCodeableConcept.coding"
                    )
                ],
                supportingGenomicVariantsIds=[
                    id
                    for id in rec.fhirpath_values(
                        "extension('supportingEvidence').valueReference.reference.getValue().replace('Observation/','')"
                    )
                    if models.GenomicVariant.objects.filter(id=id).exists()
                ],
                supportingGenomicSignaturesIds=[
                    id
                    for id in rec.fhirpath_values(
                        "extension('supportingEvidence').valueReference.reference.getValue().replace('Observation/','')"
                    )
                    if models.GenomicSignature.objects.filter(id=id).exists()
                ],
                supportingTumorMarkersIds=[
                    id
                    for id in rec.fhirpath_values(
                        "extension('supportingEvidence').valueReference.reference.getValue().replace('Observation/','')"
                    )
                    if models.TumorMarker.objects.filter(id=id).exists()
                ],
            )
            data.append(
                (
                    models.MolecularTherapeuticRecommendation.objects.filter(
                        molecular_tumor_board__id=obj.id, id=rec.id
                    ).first()
                    or models.MolecularTherapeuticRecommendation(
                        molecular_tumor_board=get_object_or_404(
                            models.MolecularTumorBoard, id=obj.id
                        )
                    ),
                    payload,
                )
            )
        return data

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.MolecularTumorBoard
    ) -> fhir.OnconovaMolecularTumorBoardReview:

        if obj.category != TumorBoardSpecialties.MOLECULAR:
            raise ValueError(
                "Only molecular tumor boards are supported by this profile"
            )

        resource = fhir.OnconovaMolecularTumorBoardReview.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.performedDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.code = fhir.OnconovaMolecularTumorBoardReviewCode(
            extension=[
                fhir.TumorBoardSpecialization(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        Coding(
                            code="C20826",
                            system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                            display="Molecular Diagnosis",
                        )
                    )
                )
            ]
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
        resource.extension = resource.extension or []
        if obj.conductedMolecularComparison is not None:
            ext = fhir.MolecularTumorBoardMolecularComparison(
                extension=[
                    fhir.MolecularTumorBoardMolecularComparisonConducted(
                        valueBoolean=obj.conductedMolecularComparison,
                    ),
                ]
            )
            assert ext.extension
            if obj.molecularComparisonMatchId is not None:
                ext.extension.append(
                    fhir.MolecularTumorBoardMolecularComparisonMatchedReference(
                        valueReference=Reference(
                            reference=f"Condition/{obj.molecularComparisonMatchId}"
                        )
                    )
                )
            resource.extension.append(ext)
        if obj.conductedCupCharacterization is not None:
            ext = fhir.MolecularTumorBoardCUPCharacterization(
                extension=[
                    fhir.MolecularTumorBoardCUPCharacterizationConducted(
                        valueBoolean=obj.conductedCupCharacterization,
                    ),
                ],
            )
            assert ext.extension
            if obj.characterizedCup is not None:
                ext.extension.append(
                    fhir.MolecularTumorBoardCUPCharacterizationSuccess(
                        valueBoolean=obj.characterizedCup,
                    )
                )
            resource.extension.append(ext)
        for rec in obj.therapeuticRecommendations or []:
            recommendation = (
                fhir.MolecularTumorBoardTherapeuticRecommendation.model_construct()
            )
            recommendation.extension = []
            if rec.expectedEffect:
                recommendation.extension.append(
                    fhir.MolecularTumorBoardTherapeuticRecommendationExpectedEffect(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            rec.expectedEffect
                        )
                    )
                )
            if rec.clinicalTrial:
                recommendation.extension.append(
                    fhir.MolecularTumorBoardTherapeuticRecommendationClinicalTrial(
                        valueString=rec.clinicalTrial
                    )
                )
            if rec.offLabelUse is not None:
                recommendation.extension.append(
                    fhir.MolecularTumorBoardTherapeuticRecommendationOffLabelUse(
                        valueBoolean=rec.offLabelUse
                    )
                )
            if rec.withinSoc is not None:
                recommendation.extension.append(
                    fhir.MolecularTumorBoardTherapeuticRecommendationWithinSoc(
                        valueBoolean=rec.withinSoc
                    )
                )
            for drug in rec.drugs or []:
                recommendation.extension.append(
                    fhir.MolecularTumorBoardTherapeuticRecommendationMedication(
                        valueCodeableConcept=construct_fhir_codeable_concept(drug)
                    )
                )
            for ref in (
                (rec.supportingGenomicVariantsIds or [])
                + (rec.supportingGenomicSignaturesIds or [])
                + (rec.supportingTumorMarkersIds or [])
            ):
                recommendation.extension.append(
                    fhir.MolecularTumorBoardTherapeuticRecommendationSupportingEvidence(
                        valueReference=Reference(reference=f"Observation/{ref}")
                    )
                )

        return resource
