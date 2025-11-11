from fhircraft.fhir.resources.datatypes.R4.complex_types import (
    CodeableConcept,
    Duration,
    Reference,
)
from ninja.schema import DjangoGetter
from pydantic import model_validator

from onconova.core.schemas import BaseSchema
from onconova.interoperability.fhir.models import CancerPatient as fhir
from onconova.oncology import models, schemas


class OnconovaCancerPatient(BaseSchema, fhir.OnconovaCancerPatient):

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.PatientCase) -> fhir.OnconovaCancerPatient:
        data = obj.model_dump()
        data.update(
            id=str(obj.id),
            _name=[fhir.OnconovaCancerPatientName()],
            gender=obj.gender.code,
            birthDate=obj.dateOfBirth,
            deceasedDateTime=obj.dateOfDeath,
            identifier=[
                fhir.OnconovaCancerPatientOnconovaIdentifier(
                    value=obj.pseudoidentifier
                ),
                fhir.OnconovaCancerPatientClinicalIdentifier(
                    value=obj.clinicalIdentifier, system=obj.clinicalCenter
                ),
            ],
            extension=(
                [fhir.USCoreBirthSexExtension(valueCode=obj.sexAtBirth.code)]
                if obj.sexAtBirth
                else []
            ),
        )
        resource = fhir.OnconovaCancerPatient.model_validate(data)
        resource.extension = []
        if obj.sexAtBirth is not None:
            resource.extension.append(
                fhir.USCoreBirthSexExtension(valueCode=obj.sexAtBirth.code)
            )
        if obj.genderIdentity is not None:
            resource.extension.append(
                fhir.USCoreGenderIdentityExtension(
                    valueCodeableConcept=CodeableConcept(
                        **obj.genderIdentity.model_dump()
                    )
                )
            )
        if obj.age is not None:
            resource.extension.append(fhir.AgeExtension(valueInteger=obj.age))
        if obj.ageAtDiagnosis is not None:
            resource.extension.append(
                fhir.AgeAtDiagnosis(valueInteger=obj.ageAtDiagnosis)
            )
        if obj.dataCompletionRate is not None:
            resource.extension.append(
                fhir.DataCompletionRate(valueDecimal=obj.dataCompletionRate)
            )
        if obj.contributors is not None:
            resource.extension.extend(
                [
                    fhir.Contributors(
                        valueReference=Reference(type="Person", display=contributor)
                    )
                    for contributor in obj.contributors
                ]
            )
        if obj.causeOfDeath is not None:
            resource.extension.append(
                fhir.CauseOfDeath(
                    valueCodeableConcept=CodeableConcept(
                        **obj.causeOfDeath.model_dump()
                    )
                )
            )
        if obj.endOfRecords is not None:
            resource.extension.append(fhir.EndOfRecords(valueDate=obj.endOfRecords))

        if obj.overallSurvival is not None:
            resource.extension.append(
                fhir.OverallSurvival(
                    valueDuration=Duration(
                        value=obj.overallSurvival,
                        unit="months",
                        system="http://unitsofmeasure.org",
                        code="m",
                    )
                )
            )
        if obj.race is not None:
            resource.extension.append(
                fhir.USCoreRaceExtension(
                    extension=[
                        fhir.USCoreRaceExtensionOmbCategory(
                            valueCodeableConcept=CodeableConcept(
                                **obj.race.model_dump()
                            )
                        )
                    ]
                )
            )
        return resource

    @model_validator(mode="before")
    @classmethod
    def pre_validator(cls, obj):
        if isinstance(obj, DjangoGetter):
            obj = schemas.PatientCase.model_validate(obj)
            return cls.onconova_to_fhir(obj)
        elif isinstance(obj, schemas.PatientCase):
            return cls.onconova_to_fhir(obj)
        return obj
