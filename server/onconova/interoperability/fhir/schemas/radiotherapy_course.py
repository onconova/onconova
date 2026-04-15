from fhircraft.fhir.resources.datatypes.R4.complex import (
    Narrative,
    Reference,
    Coding,
    Quantity,
)
from fhircraft.fhir.resources.datatypes.R4.core import BodyStructure
from django.shortcuts import get_object_or_404
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
    MappingRule,
)
from onconova.interoperability.fhir.models import RadiotherapyCourseSummary as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.oncology.models.surgery import SurgeryIntentChoices
from onconova.core.schemas import CodedConcept, Period, Measure
from uuid import uuid4


class RadiotherapyCourseSummaryProfile(
    OnconovaFhirBaseSchema, fhir.OnconovaRadiotherapyCourseSummary
):

    __model__ = models.Radiotherapy
    __schema__ = schemas.Radiotherapy

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaRadiotherapyCourseSummary
    ) -> schemas.RadiotherapyCreate:
        return schemas.RadiotherapyCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single(
                "Procedure.subject.reference.getValue()"
            ).replace("Patient/", ""),
            period=Period.model_validate(
                obj.fhirpath_single("Procedure.performedPeriod").model_dump()
            ),
            intent=cls.map_to_internal(
                "TreatmentIntents",
                obj.fhirpath_single(
                    "Procedure.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-procedure-intent').valueCodeableConcept.coding"
                ),
            ),
            targetedEntitiesIds=obj.fhirpath_values(
                "Procedure.reasonReference.reference.getValue().replace('Condition/','')"
            ),
            therapyLineId=obj.fhirpath_single(
                "Procedure.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-therapy-line-reference').valueReference.reference.getValue().replace('List/','')"
            ),
            sessions=obj.fhirpath_single(
                "Procedure.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-radiotherapy-sessions').valueUnsignedInt.getValue()"
            ),
        )

    @classmethod
    def fhir_to_onconova_related(
        cls, obj: fhir.OnconovaRadiotherapyCourseSummary
    ) -> list[
        tuple[models.RadiotherapyDosage, schemas.RadiotherapyDosageCreate]
        | tuple[models.RadiotherapySetting, schemas.RadiotherapySettingCreate]
    ]:
        data = []
        dosages: list[fhir.RadiotherapyDoseDeliveredToVolume] = obj.fhirpath_values(
            "Procedure.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-radiotherapy-dose-delivered-to-volume')"
        )
        for dosage in dosages:
            volume_reference = dosage.fhirpath_single(
                "extension('volume').valueReference.reference.getValue().substring(1)"
            )
            volume = obj.fhirpath_single(f"contained.where(id='{volume_reference}')")
            payload = schemas.RadiotherapyDosageCreate(
                dose=(
                    Measure(value=str(dose.value), unit=str(dose.code))  # type: ignore
                    if (
                        dose := dosage.fhirpath_single(
                            "extension('totalDoseDelivered').valueQuantity"
                        )
                    )
                    else None
                ),
                fractions=dosage.fhirpath_single(
                    "extension('fractionsDelivered').valueUnsignedInt.getValue()"
                ),
                irradiatedVolume=CodedConcept.model_validate(
                    volume.fhirpath_single("location.coding").model_dump()
                ),
                irradiatedVolumeMorphology=(
                    CodedConcept.model_validate(coding.model_dump())
                    if (coding := volume.fhirpath_single("morphology.coding"))
                    else None
                ),
                irradiatedVolumeQualifier=(
                    CodedConcept.model_validate(coding.model_dump())
                    if (coding := volume.fhirpath_single("locationQualifier.coding"))
                    else None
                ),
            )
            data.append(
                (
                    models.RadiotherapyDosage.objects.filter(
                        radiotherapy__id=str(obj.id), pk=str(dosage.id)
                    ).first()
                    or models.RadiotherapyDosage(
                        radiotherapy=get_object_or_404(models.Radiotherapy, id=obj.id)
                    ),
                    payload,
                )
            )

        settings: list[fhir.RadiotherapyDoseDeliveredToVolume] = obj.fhirpath_values(
            "Procedure.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-radiotherapy-modality-and-technique')"
        )
        for setting in settings:
            payload = schemas.RadiotherapySettingCreate(
                modality=CodedConcept.model_validate(
                    setting.fhirpath_single(
                        "extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-radiotherapy-modality').valueCodeableConcept.coding"
                    ).model_dump()
                ),
                technique=CodedConcept.model_validate(
                    setting.fhirpath_single(
                        "extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-radiotherapy-technique').valueCodeableConcept.coding"
                    ).model_dump()
                ),
            )
            data.append(
                (
                    models.RadiotherapySetting.objects.filter(
                        radiotherapy__id=obj.id, id=setting.id
                    ).first()
                    or models.RadiotherapySetting(
                        radiotherapy=get_object_or_404(models.Radiotherapy, id=obj.id)
                    ),
                    payload,
                )
            )
        return data

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.Radiotherapy
    ) -> fhir.OnconovaRadiotherapyCourseSummary:
        resource = fhir.OnconovaRadiotherapyCourseSummary.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.performedPeriod = fhir.Period(
            start=obj.period.start.isoformat() if obj.period.start else None,
            end=obj.period.end.isoformat() if obj.period.end else None,
        )
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.reasonReference = [
            Reference(
                reference=f"Condition/{conditionId}",
            )
            for conditionId in obj.targetedEntitiesIds or []
        ]
        resource.extension = [
            fhir.RadiotherapySessions(valueUnsignedInt=obj.sessions),
            fhir.ProcedureIntent(
                valueCodeableConcept=construct_fhir_codeable_concept(
                    cls.map_to_fhir("TreatmentIntents", obj.intent)
                )
            ),
        ]
        if obj.terminationReason:
            resource.extension.append(
                fhir.TreatmentTerminationReason(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        obj.terminationReason
                    )
                )
            )
        if obj.therapyLineId:
            resource.extension.append(
                fhir.TherapyLineReference(
                    valueReference=Reference(reference=f"List/{obj.therapyLineId}")
                )
            )
        for _index, _obj in enumerate(obj.dosages):

            internal_id = f"volume-{_index}"
            volume = BodyStructure(
                id=internal_id,
                location=construct_fhir_codeable_concept(_obj.irradiatedVolume),
                morphology=(
                    construct_fhir_codeable_concept(_obj.irradiatedVolumeMorphology)
                    if _obj.irradiatedVolumeMorphology
                    else None
                ),
                locationQualifier=(
                    [construct_fhir_codeable_concept(_obj.irradiatedVolumeQualifier)]
                    if _obj.irradiatedVolumeQualifier
                    else None
                ),
                patient=resource.subject,
            )
            resource.contained = resource.contained or []
            resource.contained.append(volume)  # type: ignore

            # Construct reference
            ref = Reference.model_construct()
            ref.reference = f"#{internal_id}"
            ext = fhir.RadiotherapyDoseDeliveredToVolumeVolume.model_construct()
            ext.valueReference = ref
            dosage = fhir.RadiotherapyDoseDeliveredToVolume(
                id=str(_obj.id),
                extension=[ext],
            )
            dosage.extension = dosage.extension or []
            if _obj.fractions:
                dosage.extension.append(
                    fhir.RadiotherapyDoseDeliveredToVolumeFractionsDelivered(
                        valueUnsignedInt=_obj.fractions
                    )
                )
            if _obj.dose:
                dosage.extension.append(
                    fhir.RadiotherapyDoseDeliveredToVolumeTotalDoseDelivered(
                        valueQuantity=Quantity(
                            value=_obj.dose.value * 100,
                            code="cGy",
                            system="http://unitsofmeasure.org",
                        )
                    )
                )

            resource.extension.append(dosage)

        for _obj in obj.settings:
            setting = fhir.RadiotherapyModalityAndTechnique(
                id=str(_obj.id),
                extension=[
                    fhir.RadiotherapyModality(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            _obj.modality
                        )
                    ),
                    fhir.RadiotherapyTechnique(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            _obj.technique
                        )
                    ),
                ],
            )
            resource.extension.append(setting)
        return resource


RadiotherapyCourseSummaryProfile.register_mapping(
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
