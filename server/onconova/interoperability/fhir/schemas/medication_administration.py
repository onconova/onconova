from fhircraft.fhir.resources.datatypes.R4.complex import Reference, Coding
from django.shortcuts import get_object_or_404
from onconova.interoperability.fhir.schemas.base import OnconovaFhirBaseSchema, MappingRule
from onconova.interoperability.fhir.models import MedicationAdministration as fhir
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept, ucum_to_internal, internal_to_ucum
from onconova.oncology import models, schemas
from onconova.core.schemas import CodedConcept, Period, Measure
from onconova.core.measures import (
    Mass, MassPerArea, Volume, MassConcentration,
    MassConcentrationPerTime, MassPerTime, VolumePerTime, MassPerAreaPerTime
)
from onconova.oncology.models.systemic_therapy import SystemicTherapyIntentChoices

def get_unit_comparison_fhirpath(element: str, measure):
    return ' or '.join([f"{element}.code = '{internal_to_ucum(unit)}'" for unit in measure.get_units()])
    

class MedicationAdministrationProfile(OnconovaFhirBaseSchema, fhir.OnconovaMedicationAdministration):

    __model__ = models.SystemicTherapy
    __schema__ = schemas.SystemicTherapy

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaMedicationAdministration
    ) -> schemas.SystemicTherapyCreate:
        return schemas.SystemicTherapyCreate(
            caseId=obj.fhirpath_single("MedicationAdministration.subject.reference").replace(
                "Patient/", ""
            ),
            period=Period(
                start=(
                    period := obj.fhirpath_single("MedicationAdministration.effectivePeriod")
                ).start,
                end=period.end,
            ),
            intent=cls.map_to_internal(
                "TreatmentIntents",
                obj.fhirpath_single(
                    "MedicationAdministration.extension('http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-procedure-intent').valueCodeableConcept.coding"
                ),
            ),
            targetedEntitiesIds=obj.fhirpath_values(
                "MedicationAdministration.reasonReference.reference.replace('Condition/','')"
            ),
            therapyLineId=obj.fhirpath_single(
                "MedicationAdministration.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-therapy-line-reference').valueReference.reference.replace('List/','')"
            ),
            cycles=obj.fhirpath_single(
                "MedicationAdministration.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-medication-administration-cycles').valueInteger"
            ),
            adjunctiveRole=CodedConcept.model_validate(role) if (
                role:=obj.fhirpath_single(
                    "MedicationAdministration.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-medication-administration-adjunctive-role').valueCodeableConcept.coding"
                ),
            ) else None,
            terminationReason=CodedConcept.model_validate(role) if (
                role:=obj.fhirpath_single(
                    "MedicationAdministration.statusReason.coding"
                ),
            ) else None,
        )
        

    @classmethod
    def fhir_to_onconova_related(
        cls, obj: fhir.OnconovaMedicationAdministration
    ) -> list[
        tuple[models.SystemicTherapyMedication, schemas.SystemicTherapyMedicationCreate]
    ]:
        data = []

        medications = [obj, *obj.fhirpath_values("contained")]
        for medication in medications:
            payload = schemas.SystemicTherapyMedicationCreate(
                drug=CodedConcept.model_validate(
                    medication.fhirpath_single(
                        "medicationCodeableConcept.coding"
                    )
                ),
                route=CodedConcept.model_validate(
                    medication.fhirpath_single(
                        "dosage.route.coding"
                    )
                ),
                dosageMassConcentration=Measure(value=quantity.value, unit=ucum_to_internal(quantity.code)) if (
                    quantity:=medication.fhirpath_single(
                        f"dosage.where({get_unit_comparison_fhirpath('dose', MassConcentration)}).dose"
                    )
                ) else None,
                dosageMass=Measure(value=quantity.value, unit=ucum_to_internal(quantity.code)) if (
                    quantity:=medication.fhirpath_single(
                        f"dosage.where({get_unit_comparison_fhirpath('dose', Mass)}).dose"
                    )
                ) else None,
                dosageVolume=Measure(value=quantity.value, unit=ucum_to_internal(quantity.code)) if (
                    quantity:=medication.fhirpath_single(
                        f"dosage.where({get_unit_comparison_fhirpath('dose', Volume)}).dose"
                    )
                ) else None,
                dosageMassSurface=Measure(value=quantity.value, unit=ucum_to_internal(quantity.code)) if (
                    quantity:=medication.fhirpath_single(
                        f"dosage.where({get_unit_comparison_fhirpath('dose', MassPerArea)}).dose"
                    )
                ) else None,
                dosageRateMassConcentration=Measure(value=quantity.value, unit=ucum_to_internal(quantity.code)) if (
                    quantity:=medication.fhirpath_single(
                        f"dosage.where({get_unit_comparison_fhirpath('rateQuantity', MassConcentrationPerTime)}).rateQuantity"
                    )
                ) else None,
                dosageRateMass=Measure(value=quantity.value, unit=ucum_to_internal(quantity.code)) if (
                    quantity:=medication.fhirpath_single(
                        f"dosage.where({get_unit_comparison_fhirpath('rateQuantity', MassPerTime)}).rateQuantity"
                    )
                ) else None,
                dosageRateVolume=Measure(value=quantity.value, unit=ucum_to_internal(quantity.code)) if (
                    quantity:=medication.fhirpath_single(
                        f"dosage.where({get_unit_comparison_fhirpath('rateQuantity', VolumePerTime)}).rateQuantity"
                    )
                ) else None,
                dosageRateMassSurface=Measure(value=quantity.value, unit=ucum_to_internal(quantity.code)) if (
                    quantity:=medication.fhirpath_single(
                        f"dosage.where({get_unit_comparison_fhirpath('dose', MassPerAreaPerTime)}).dose"
                    )
                ) else None,
            )
            data.append(
                (
                    models.SystemicTherapyMedication.objects.filter(
                        systemic_therapy__id=obj.id, id=medication.id
                    ).first()
                    or models.SystemicTherapyMedication(
                        systemic_therapy=get_object_or_404(models.SystemicTherapy, id=obj.id)
                    ),
                    payload,
                )
            )
        return data
        
        
    @classmethod
    def construct_medication_administration(cls, obj, medication) -> fhir.OnconovaMedicationAdministration:
        resource = fhir.OnconovaMedicationAdministration.model_construct()
        resource.id = str(obj.id)
        resource.text = fhir.Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.effectivePeriod = fhir.Period(
            start=obj.period.start.isoformat() if obj.period.start else None,
            end=obj.period.end.isoformat() if obj.period.end else None,
        )
        resource.reasonReference = [
            Reference(reference=f'Condition/{conditionId}')
            for conditionId in obj.targetedEntitiesIds    
        ] if obj.targetedEntitiesIds else None    

        if obj.terminationReason:
            resource.statusReason=construct_fhir_codeable_concept(obj.terminationReason)

        resource.extension = [
                fhir.MedicationAdministrationIsPrimaryTherapy(
                    valueBoolean=obj.isAdjunctive is not None,
                ),         
                fhir.ProcedureIntent(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        cls.map_to_fhir("treatmentIntents", obj.intent)
                    )
                ),   
        ]
        if obj.cycles:
            resource.extension.append(
                fhir.MedicationAdministrationCycles(
                    valueInteger=obj.cycles
                )
            )
        if obj.adjunctiveRole:
            resource.extension.append(
                fhir.MedicationAdministrationAdjunctiveRole(
                    valueCodeableConcept=construct_fhir_codeable_concept(obj.adjunctiveRole)
                )
            )
        if obj.therapyLineId:
            resource.extension.append(
                fhir.TherapyLineReference(
                    valueReference=Reference(reference=f"List/{obj.therapyLineId}")
                )
            )
        # Process first medication
        resource.medicationCodeableConcept = construct_fhir_codeable_concept(medication.drug)
        resource.dosage = fhir.OnconovaMedicationAdministrationDosage(
            route=construct_fhir_codeable_concept(medication.route) if medication.route else None,
            dose=fhir.Quantity(value=dose.value, code=internal_to_ucum(dose.unit), system="") if (
                dose:=(
                    medication.dosageMassConcentration 
                    or medication.dosageMass 
                    or medication.dosageVolume 
                    or medication.dosageMassSurface
                ) 
            ) else None,
        rateQuantity=fhir.Quantity(value=dose.value, code=internal_to_ucum(dose.unit), system="http://unitsofmeasure.org") if (
            dose:=(
                medication.dosageRateMassConcentration 
                or medication.dosageRateMass 
                or medication.dosageRateVolume 
                or medication.dosageRateMassSurface
            ) 
        ) else None
        )
        return resource

    @classmethod
    def onconova_to_fhir(
        cls, obj: schemas.SystemicTherapy
    ) -> fhir.OnconovaMedicationAdministration:

        resource = cls.construct_medication_administration(obj, obj.medications[0])
        resource.contained = []
        for n,medication in enumerate(obj.medications[1:]):
            contained_resource = cls.construct_medication_administration(obj, medication)
            contained_resource.id = f"combined-administration-{n}"
            ref = Reference.model_construct()
            ref.reference=f"#{contained_resource.id}"

            combined = fhir.MedicationAdministrationCombinedWith.model_construct()
            combined.valueReference = ref

            resource.contained.append(contained_resource)
            resource.extension = resource.extension or []
            resource.extension.append(combined)            
        return resource



MedicationAdministrationProfile.register_mapping(
    "treatmentIntents",
    [
        MappingRule(
            SystemicTherapyIntentChoices.CURATIVE,
            Coding(
                code="373808002",
                system="http://snomed.info/sct",
                display="Curative - procedure intent",
            ),
        ),
        MappingRule(
            SystemicTherapyIntentChoices.PALLIATIVE,
            Coding(
                code="363676003",
                system="http://snomed.info/sct",
                display="Palliative  - procedure intent",
            ),
        ),
    ],
)
