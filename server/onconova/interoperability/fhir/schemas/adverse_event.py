from typing import Sequence

from fhircraft.fhir.resources.datatypes.R4.complex import (
    Date,
    Integer,
    Narrative,
    Reference,
    Coding,
    Quantity,
)
from fhircraft.fhir.resources.datatypes.R4.primitive import DateTime
from fhircraft.fhir.resources.datatypes.R4.core import (
    AdverseEventSuspectEntityCausality,
    BodyStructure,
)
from django.shortcuts import get_object_or_404
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
    MappingRule,
)
from onconova.interoperability.fhir.models import AdverseEvent as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept
from onconova.oncology.models.adverse_event import (
    AdverseEventOutcomeChoices,
    AdverseEventSuspectedCauseCausalityChoices,
    AdverseEventMitigationCategoryChoices,
)


class AdverseEventProfile(OnconovaFhirBaseSchema, fhir.OnconovaAdverseEvent):

    __model__ = models.AdverseEvent
    __schema__ = schemas.AdverseEvent

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaAdverseEvent
    ) -> schemas.AdverseEventCreate:
        return schemas.AdverseEventCreate(
            caseId=obj.fhirpath_single("AdverseEvent.subject.reference").replace(
                "Patient/", ""
            ),
            date=obj.fhirpath_single("AdverseEvent.date").value,
            event=CodedConcept.model_validate(
                obj.fhirpath_single("AdverseEvent.event.coding").model_dump()
            ),
            grade=obj.fhirpath_single(
                "AdverseEvent.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-adverse-event-ctc-grade').valueInteger"
            ).value,
            outcome=cls.map_to_internal(
                "outcome",
                obj.fhirpath_single("AdverseEvent.outcome.coding"),
            ),
            dateResolved=obj.fhirpath_single(
                "AdverseEvent.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-adverse-event-resolved-date').valueDate"
            ),
        )

    @classmethod
    def fhir_to_onconova_related(
        cls, obj: fhir.OnconovaAdverseEvent
    ) -> Sequence[
        tuple[models.AdverseEventMitigation, schemas.AdverseEventMitigationCreate]
        | tuple[
            models.AdverseEventSuspectedCause, schemas.AdverseEventSuspectedCauseCreate
        ]
    ]:
        data = []
        mitigations: list[fhir.AdverseEventMitigation] = obj.fhirpath_values(
            "AdverseEvent.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-adverse-event-mitigation')"
        )
        for mitigation in mitigations:
            payload = schemas.AdverseEventMitigationCreate(
                category=cls.map_to_internal(
                    "mitigationCategory",
                    mitigation.fhirpath_single(
                        "extension('category').valueCodeableConcept.coding"
                    ),
                ),
                adjustment=(
                    CodedConcept.model_validate(coding.model_dump())
                    if (
                        coding := mitigation.fhirpath_single(
                            "extension('adjustment').valueCodeableConcept.coding"
                        )
                    )
                    else None
                ),
                drug=(
                    CodedConcept.model_validate(coding.model_dump())
                    if (
                        coding := mitigation.fhirpath_single(
                            "extension('drug').valueCodeableConcept.coding"
                        )
                    )
                    else None
                ),
                procedure=(
                    CodedConcept.model_validate(coding.model_dump())
                    if (
                        coding := mitigation.fhirpath_single(
                            "extension('procedure').valueCodeableConcept.coding"
                        )
                    )
                    else None
                ),
                management=(
                    CodedConcept.model_validate(coding.model_dump())
                    if (
                        coding := mitigation.fhirpath_single(
                            "extension('management').valueCodeableConcept.coding"
                        )
                    )
                    else None
                ),
            )
            data.append(
                (
                    models.AdverseEventMitigation.objects.filter(
                        adverse_event__id=obj.id, id=mitigation.id
                    ).first()
                    or models.AdverseEventMitigation(
                        adverse_event=get_object_or_404(models.AdverseEvent, id=obj.id)
                    ),
                    payload,
                )
            )
        suspects: list[fhir.AdverseEventMitigation] = obj.fhirpath_values(
            "AdverseEvent.suspectedEntity"
        )
        for suspect in suspects:
            payload = schemas.AdverseEventSuspectedCauseCreate(
                causality=cls.map_to_internal(
                    "causality", suspect.fhirpath_single("causality.assessment.coding")
                ),
                radiotherapyId=(
                    id
                    if models.Radiotherapy.objects.filter(
                        id=(
                            id := suspect.fhirpath_single(
                                "instance.reference.replace('Procedure','')"
                            )
                        )
                    ).exists()
                    else None
                ),
                systemicTherapyId=(
                    id
                    if models.SystemicTherapy.objects.filter(
                        id=(
                            id := suspect.fhirpath_single(
                                "instance.reference.replace('MedicationAdministration','')"
                            )
                        )
                    ).exists()
                    else None
                ),
                surgeryId=(
                    id
                    if models.Surgery.objects.filter(
                        id=(
                            id := suspect.fhirpath_single(
                                "instance.reference.replace('Procedure','')"
                            )
                        )
                    ).exists()
                    else None
                ),
            )
            data.append(
                (
                    models.AdverseEventSuspectedCause.objects.filter(
                        adverse_event__id=obj.id, id=suspect.id
                    ).first()
                    or models.AdverseEventSuspectedCause(
                        adverse_event=get_object_or_404(models.AdverseEvent, id=obj.id)
                    ),
                    payload,
                )
            )

        return data

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.AdverseEvent) -> fhir.OnconovaAdverseEvent:
        resource = fhir.OnconovaAdverseEvent.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.date = DateTime(value=obj.date.isoformat())
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.event = construct_fhir_codeable_concept(obj.event)
        resource.outcome = construct_fhir_codeable_concept(
            cls.map_to_fhir("outcome", obj.outcome)
        )
        resource.extension = [
            fhir.AdverseEventCTCGrade(valueInteger=obj.grade),
        ]
        assert resource.extension
        if obj.dateResolved:
            resource.extension.append(
                fhir.AdverseEventResolvedDate(
                    valueDate=Date(value=obj.dateResolved.isoformat())
                )
            )
        resource.suspectEntity = []
        for cause in obj.suspectedCauses:
            if cause.systemicTherapyId:
                ref = f"MedicationAdministration/{cause.systemicTherapyId}"
            elif cause.radiotherapyId:
                ref = f"Procedure/{cause.radiotherapyId}"
            elif cause.surgeryId:
                ref = f"Procedure/{cause.surgeryId}"
            elif cause.medicationId:
                continue
            else:
                raise ValueError(
                    f"Suspected cause with id {cause.id} has no valid reference"
                )
            resource.suspectEntity.append(
                fhir.OnconovaAdverseEventSuspectEntity(
                    id=str(cause.id),
                    instance=Reference(reference=ref),
                    causality=(
                        [
                            AdverseEventSuspectEntityCausality(
                                assessment=construct_fhir_codeable_concept(
                                    cls.map_to_fhir("causality", cause.causality)
                                )
                            )
                        ]
                        if cause.causality
                        else None
                    ),
                )
            )
        for mitigation in obj.mitigations:
            mitigation_extensions: list[fhir.Extension] = [
                fhir.AdverseEventMitigationCategory(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        cls.map_to_fhir("mitigationCategory", mitigation.category)
                    )
                )
            ]
            if mitigation.adjustment:
                mitigation_extensions.append(
                    fhir.AdverseEventMitigationAdjustment(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            mitigation.adjustment
                        )
                    )
                )
            if mitigation.drug:
                mitigation_extensions.append(
                    fhir.AdverseEventMitigationDrug(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            mitigation.drug
                        )
                    )
                )
            if mitigation.procedure:
                mitigation_extensions.append(
                    fhir.AdverseEventMitigationProcedure(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            mitigation.procedure
                        )
                    )
                )
            if mitigation.management:
                mitigation_extensions.append(
                    fhir.AdverseEventMitigationManagement(
                        valueCodeableConcept=construct_fhir_codeable_concept(
                            mitigation.management
                        )
                    )
                )
            resource.extension.append(
                fhir.AdverseEventMitigation(
                    id=str(mitigation.id),
                    extension=mitigation_extensions,
                )
            )

        return resource


AdverseEventProfile.register_mapping(
    "outcome",
    [
        MappingRule(
            AdverseEventOutcomeChoices.RESOLVED,
            Coding(
                code="resolved",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            ),
        ),
        MappingRule(
            AdverseEventOutcomeChoices.RESOLVED_WITH_SEQUELAE,
            Coding(
                code="resolvedWithSequelae",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            ),
        ),
        MappingRule(
            AdverseEventOutcomeChoices.RECOVERING,
            Coding(
                code="recovering",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            ),
        ),
        MappingRule(
            AdverseEventOutcomeChoices.ONGOING,
            Coding(
                code="ongoing",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            ),
        ),
        MappingRule(
            AdverseEventOutcomeChoices.FATAL,
            Coding(
                code="fatal",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            ),
        ),
        MappingRule(
            AdverseEventOutcomeChoices.UNKNOWN,
            Coding(
                code="unknown",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-outcome",
            ),
        ),
    ],
)


AdverseEventProfile.register_mapping(
    "mitigationCategory",
    [
        MappingRule(
            AdverseEventMitigationCategoryChoices.ADJUSTMENT,
            Coding(
                code="C49157",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="Adjustment",
            ),
        ),
        MappingRule(
            AdverseEventMitigationCategoryChoices.PHARMACOLOGICAL,
            Coding(
                code="C49158",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="Drug",
            ),
        ),
        MappingRule(
            AdverseEventMitigationCategoryChoices.PROCEDIRE,
            Coding(
                code="C49159",
                system="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl",
                display="Procedure",
            ),
        ),
    ],
)

AdverseEventProfile.register_mapping(
    "causality",
    [
        MappingRule(
            AdverseEventSuspectedCauseCausalityChoices.UNRELATED,
            Coding(
                code="Unassessable-Unclassifiable",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-causality-assess",
            ),
        ),
        MappingRule(
            AdverseEventSuspectedCauseCausalityChoices.UNLEKELY_RELATED,
            Coding(
                code="Unlikely",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-causality-assess",
            ),
        ),
        MappingRule(
            AdverseEventSuspectedCauseCausalityChoices.POSSIBLY_RELATED,
            Coding(
                code="Possible",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-causality-assess",
            ),
        ),
        MappingRule(
            AdverseEventSuspectedCauseCausalityChoices.PROBABLY_RELATED,
            Coding(
                code="Probably-Likely",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-causality-assess",
            ),
        ),
        MappingRule(
            AdverseEventSuspectedCauseCausalityChoices.DEFINITELY_RELATED,
            Coding(
                code="Certain",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-causality-assess",
            ),
        ),
        MappingRule(
            AdverseEventSuspectedCauseCausalityChoices.CONDITIONALLY_RELATED,
            Coding(
                code="Conditional-Classified",
                system="http://terminology.hl7.org/CodeSystem/adverse-event-causality-assess",
            ),
        ),
    ],
)
