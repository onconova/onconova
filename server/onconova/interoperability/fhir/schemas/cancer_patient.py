from fhircraft.fhir.resources.datatypes.R4.complex import (
    Duration,
    Reference,
)
from ninja.schema import DjangoGetter
from pydantic import ValidationError, model_validator

from onconova.core.schemas import BaseSchema, CodedConcept
from onconova.interoperability.fhir.models import CancerPatient as fhir
from onconova.oncology import models, schemas
from onconova.oncology.models.patient_case import (
    PatientCaseConsentStatusChoices,
    PatientCaseVitalStatusChoices,
)

CONSENT_STATUS_MAPPING = {
    "valid": PatientCaseConsentStatusChoices.VALID,
    "revoked": PatientCaseConsentStatusChoices.REVOKED,
    "unknown": PatientCaseConsentStatusChoices.UNKNOWN,
}
VITAL_STATUS_MAPPING = {
    PatientCaseVitalStatusChoices.ALIVE: fhir.Coding(
        code="438949009", system="http://snomed.info/sct", display="Alive"
    ),
    PatientCaseVitalStatusChoices.DECEASED: fhir.Coding(
        code="419099009", system="http://snomed.info/sct", display="Deceased"
    ),
    PatientCaseVitalStatusChoices.UNKNOWN: fhir.Coding(
        code="261665006", system="http://snomed.info/sct", display="Unknown"
    ),
}


class OnconovaCancerPatient(BaseSchema, fhir.OnconovaCancerPatient):

    @classmethod
    def _map_to_fhir_vital_status(
        cls, value: PatientCaseVitalStatusChoices
    ) -> fhir.CodeableConcept:
        if value is None:
            return None
        return fhir.CodeableConcept(coding=[VITAL_STATUS_MAPPING[value]])

    @classmethod
    def _map_to_onconova_vital_status(
        cls, value: fhir.Coding
    ) -> PatientCaseVitalStatusChoices:
        if value is None:
            return PatientCaseVitalStatusChoices.UNKNOWN
        for key, coding in VITAL_STATUS_MAPPING.items():
            if coding.code == value.code and coding.system == value.system:
                return key
        else:
            raise ValidationError(
                f"Cannot map vital status coding: code={value.code}, system={value.system}"
            )

    @classmethod
    def _map_to_fhir_consent_status(cls, value: PatientCaseConsentStatusChoices) -> str:
        if value is None:
            return "unknown"
        for key, mapping in CONSENT_STATUS_MAPPING.items():
            if mapping == value:
                return key
        else:
            raise ValidationError(f"Cannot map consent status: {value}")

    @classmethod
    def _map_to_onconova_consent_status(
        cls, value: str
    ) -> PatientCaseConsentStatusChoices:
        if value is None:
            return PatientCaseConsentStatusChoices.UNKNOWN
        for key, mapping in CONSENT_STATUS_MAPPING.items():
            if key == value:
                return mapping
        else:
            raise ValidationError(f"Cannot map consent status: {value}")

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaCancerPatient
    ) -> schemas.PatientCaseCreate:
        return schemas.PatientCaseCreate(
            externalSource=None,
            externalSourceId=None,
            clinicalCenter=obj.fhirpath_single(
                "Patient.identifier.where(type.coding.code='MR').system"
            ),
            clinicalIdentifier=obj.fhirpath_single(
                "Patient.identifier.where(type.coding.code='MR').value"
            ),
            consentStatus=cls._map_to_onconova_consent_status(
                obj.fhirpath_single(
                    "Patient.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-consent-status').valueCode"
                )
            ),
            vitalStatus=cls._map_to_onconova_vital_status(
                obj.fhirpath_single(
                    "Patient.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-vital-status').valueCodeableConcept.coding"
                )
            ),
            gender=CodedConcept(
                code=obj.fhirpath_single("Patient.gender"),
                system="http://hl7.org/fhir/administrative-gender",
            ),
            race=(
                CodedConcept(**coding)
                if (
                    coding := obj.fhirpath_single(
                        "Patient.extension('http://hl7.org/fhir/us/core/StructureDefinition/us-core-race').extension('ombCategory').valueCoding"
                    )
                )
                else None
            ),
            sexAtBirth=CodedConcept(
                code=obj.fhirpath_single(
                    "Patient.extension('http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex').valueCode"
                ),
                system="http://hl7.org/fhir/administrative-gender",
            ),
            dateOfBirth=obj.fhirpath_single("Patient.birthDate"),
            endOfRecords=obj.fhirpath_single(
                "Patient.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-end-of-records').valueDate"
            ),
            dateOfDeath=obj.fhirpath_single("Patient.deceasedDateTime"),
            causeOfDeath=(
                CodedConcept(**coding)
                if (
                    coding := obj.fhirpath_single(
                        "Patient.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-cause-of-death').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            genderIdentity=None,
        )

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
                    valueCodeableConcept=fhir.CodeableConcept(
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
        if obj.contributors is not None and len(obj.contributors) > 0:
            resource.extension.extend(
                [
                    fhir.Contributors(
                        valueReference=Reference(type="Person", display=contributor)
                    )
                    for contributor in obj.contributors
                ]
            )
        if obj.consentStatus is not None:
            resource.extension.append(
                fhir.ConsentStatus(
                    valueCode=cls._map_to_fhir_consent_status(obj.consentStatus)
                )
            )
        if obj.vitalStatus is not None:
            resource.extension.append(
                fhir.VitalStatus(
                    valueCodeableConcept=cls._map_to_fhir_vital_status(obj.vitalStatus)
                )
            )
        if obj.causeOfDeath is not None:
            resource.extension.append(
                fhir.CauseOfDeath(
                    valueCodeableConcept=fhir.CodeableConcept(
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
                            valueCodeableConcept=fhir.CodeableConcept(
                                **obj.race.model_dump()
                            )
                        )
                    ]
                )
            )
        assert resource.meta is not None
        resource.meta.lastUpdated = obj.updatedAt
        return resource

    @model_validator(mode="before")
    @classmethod
    def pre_validator(cls, obj):
        if isinstance(obj, models.PatientCase):
            obj = schemas.PatientCase.model_validate(obj)
        if isinstance(obj, DjangoGetter) and isinstance(obj._obj, models.PatientCase):
            obj = schemas.PatientCase.model_validate(obj)
            return cls.onconova_to_fhir(obj)
        elif isinstance(obj, schemas.PatientCase):
            return cls.onconova_to_fhir(obj)
        return obj
