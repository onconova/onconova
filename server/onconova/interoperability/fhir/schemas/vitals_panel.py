from fhircraft.fhir.resources.datatypes.R4.complex import (
    Narrative,
    Reference,
    Quantity,
    Coding,
)
from onconova.interoperability.fhir.schemas.base import (
    OnconovaFhirBaseSchema,
)
from fhircraft.fhir.resources.datatypes.R4.core import Observation, ObservationComponent
from onconova.interoperability.fhir.models import VitalSignsPanel as fhir
from onconova.interoperability.fhir.utils import (
    construct_fhir_codeable_concept,
    internal_to_ucum,
)
from onconova.oncology import models, schemas
from onconova.core.measures import Mass, Temperature, Distance, Pressure, MassPerArea
from onconova.core.schemas import Measure


class VitalsPanelProfile(OnconovaFhirBaseSchema, fhir.OnconovaVitalSignsPanel):

    __model__ = models.Vitals
    __schema__ = schemas.Vitals

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaVitalSignsPanel
    ) -> schemas.VitalsCreate:
        return schemas.VitalsCreate(
            externalSource=None,
            externalSourceId=None,
            caseId=obj.fhirpath_single("Observation.subject.reference").replace(
                "Patient/", ""
            ),
            date=obj.fhirpath_single("Observation.effectiveDateTime"),
            temperature=(
                Measure(
                    value=temperature.value,
                    unit=(
                        "celsius"
                        if internal_to_ucum(temperature.code) == "Cel"
                        else "fahrenheit"
                    ),
                )
                if (
                    temperature := obj.fhirpath_single(
                        "Observation.contained.where(code.coding.code='8310-5').valueQuantity"
                    )
                )
                else None
            ),
            height=(
                Measure(
                    value=height.value / 100,
                    unit="m",
                )
                if (
                    height := obj.fhirpath_single(
                        "Observation.contained.where(code.coding.code='8302-2').valueQuantity"
                    )
                )
                else None
            ),
            weight=(
                Measure(
                    value=weight.value,
                    unit="kg",
                )
                if (
                    weight := obj.fhirpath_single(
                        "Observation.contained.where(code.coding.code='29463-7').valueQuantity"
                    )
                )
                else None
            ),
            bloodPressureSystolic=(
                Measure(
                    value=bloodPressureSystolic.value,
                    unit="mmHg",
                )
                if (
                    bloodPressureSystolic := obj.fhirpath_single(
                        "Observation.contained.where(code.coding.code='85354-9').component.where(code.coding.code='8480-6').valueQuantity"
                    )
                )
                else None
            ),
            bloodPressureDiastolic=(
                Measure(
                    value=bloodPressureDiastolic.value,
                    unit="mmHg",
                )
                if (
                    bloodPressureDiastolic := obj.fhirpath_single(
                        "Observation.contained.where(code.coding.code='85354-9').component.where(code.coding.code='8462-4').valueQuantity"
                    )
                )
                else None
            ),
        )

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.Vitals) -> fhir.OnconovaVitalSignsPanel:
        resource = fhir.OnconovaVitalSignsPanel.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.effectiveDateTime = obj.date.isoformat()
        resource.subject = Reference(
            reference=f"Patient/{obj.caseId}",
        )
        resource.contained = []
        resource.hasMember = []
        common = {
            "subject": resource.subject,
            "effectiveDateTime": resource.effectiveDateTime,
            "category": [
                construct_fhir_codeable_concept(
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="vital-signs",
                    )
                )
            ],
        }
        if obj.temperature:
            value = Temperature(**{obj.temperature.unit: obj.temperature.value}).celsius
            temperature = Observation(
                **common,
                id=f"{obj.id}/temperature",
                code=construct_fhir_codeable_concept(
                    Coding(
                        system="http://loinc.org",
                        code="8310-5",
                        display="Body temperature",
                    )
                ),
                valueQuantity=Quantity(
                    value=value,
                    system="http://unitsofmeasure.org",
                    code="Cel",
                ),
            )
            resource.contained.append(temperature)
            resource.hasMember.append(Reference(reference=f"#{temperature.id}"))
        if obj.bodyMassIndex:
            value = MassPerArea(
                **{obj.bodyMassIndex.unit: obj.bodyMassIndex.value}
            ).kg__square_meter
            bmi = Observation(
                **common,
                id=f"{obj.id}/bmi",
                valueQuantity=Quantity(
                    value=value,
                    system="http://unitsofmeasure.org",
                    code="kg/m2",
                ),
                code=construct_fhir_codeable_concept(
                    Coding(
                        system="http://loinc.org",
                        code="39156-5",
                        display="Body mass index (BMI) [Ratio]",
                    )
                ),
            )
            resource.contained.append(bmi)
            resource.hasMember.append(Reference(reference=f"#{bmi.id}"))
        if obj.height:
            value = Distance(**{obj.height.unit: obj.height.value}).cm
            height = Observation(
                **common,
                id=f"{obj.id}/height",
                valueQuantity=Quantity(
                    value=value,
                    code="cm",
                    system="http://unitsofmeasure.org",
                ),
                code=construct_fhir_codeable_concept(
                    Coding(
                        system="http://loinc.org",
                        code="8302-2",
                        display="Body height",
                    )
                ),
            )
            resource.contained.append(height)
            resource.hasMember.append(Reference(reference=f"#{height.id}"))
        if obj.weight:
            value = Mass(**{obj.weight.unit: obj.weight.value}).kg
            weight = Observation(
                **common,
                id=f"{obj.id}/weight",
                valueQuantity=Quantity(
                    value=value,
                    system="http://unitsofmeasure.org",
                    code="kg",
                ),
                code=construct_fhir_codeable_concept(
                    Coding(
                        system="http://loinc.org",
                        code="29463-7",
                        display="Body weight",
                    )
                ),
            )
            resource.contained.append(weight)
            resource.hasMember.append(Reference(reference=f"#{weight.id}"))
        if obj.bloodPressureSystolic:
            bp_systolic = Observation(
                **common,
                id=f"{obj.id}/bloodPressureSystolic",
                valueQuantity=Quantity(
                    value=obj.bloodPressureSystolic.value,
                    unit=obj.bloodPressureSystolic.unit,
                    system="http://unitsofmeasure.org",
                    code="mmHg",
                ),
                code=construct_fhir_codeable_concept(
                    Coding(
                        system="http://loinc.org",
                        code="8480-6",
                        display="Systolic blood pressure",
                    )
                ),
            )
            resource.contained.append(bp_systolic)
            resource.hasMember.append(Reference(reference=f"#{bp_systolic.id}"))
        if obj.bloodPressureDiastolic or obj.bloodPressureSystolic:
            blood_pressure = Observation(
                **common,
                id=f"{obj.id}/bloodPressure",
                code=construct_fhir_codeable_concept(
                    Coding(
                        system="http://loinc.org",
                        code="85354-9",
                        display="Blood pressure panel",
                    )
                ),
            )
            blood_pressure.component = []
            if obj.bloodPressureDiastolic:
                value = Pressure(
                    **{
                        obj.bloodPressureDiastolic.unit: obj.bloodPressureDiastolic.value
                    }
                ).mmHg
                blood_pressure.component.append(
                    ObservationComponent(
                        code=construct_fhir_codeable_concept(
                            Coding(
                                system="http://loinc.org",
                                code="8462-4",
                                display="Diastolic blood pressure",
                            )
                        ),
                        valueQuantity=Quantity(
                            value=value,
                            system="http://unitsofmeasure.org",
                            code="mm[Hg]",
                        ),
                    )
                )
            if obj.bloodPressureSystolic:
                value = Pressure(
                    **{obj.bloodPressureSystolic.unit: obj.bloodPressureSystolic.value}
                ).mmHg
                blood_pressure.component.append(
                    ObservationComponent(
                        code=construct_fhir_codeable_concept(
                            Coding(
                                system="http://loinc.org",
                                code="8480-6",
                                display="Systolic blood pressure",
                            )
                        ),
                        valueQuantity=Quantity(
                            value=value,
                            system="http://unitsofmeasure.org",
                            code="mm[Hg]",
                        ),
                    ),
                )
            resource.contained.append(blood_pressure)
            resource.hasMember.append(Reference(reference=f"#{blood_pressure.id}"))
        return resource
