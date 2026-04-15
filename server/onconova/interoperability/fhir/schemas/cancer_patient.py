from fhircraft.fhir.resources.datatypes.R4.complex import Duration, Reference, Narrative
from onconova.interoperability.fhir.schemas.base import (
    MappingRule,
    OnconovaFhirBaseSchema,
)
from onconova.core.schemas import CodedConcept
from onconova.interoperability.fhir.models import CancerPatient as fhir
from onconova.oncology import models, schemas
from onconova.oncology.models.patient_case import (
    PatientCaseConsentStatusChoices,
    PatientCaseVitalStatusChoices,
)
from onconova.interoperability.fhir.utils import construct_fhir_codeable_concept


class CancerPatientProfile(OnconovaFhirBaseSchema, fhir.OnconovaCancerPatient):

    __model__ = models.PatientCase
    __schema__ = schemas.PatientCase

    @classmethod
    def _get_gender_codesystem(cls) -> str:
        return "http://hl7.org/fhir/administrative-gender"

    @classmethod
    def _get_birthsex_codesystem(cls) -> str:
        return "http://hl7.org/fhir/administrative-gender"

    @classmethod
    def fhir_to_onconova(
        cls, obj: fhir.OnconovaCancerPatient
    ) -> schemas.PatientCaseCreate:
        return schemas.PatientCaseCreate(
            externalSource=None,
            externalSourceId=None,
            clinicalCenter=obj.fhirpath_single(
                "Patient.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-cancer-patient-clinical-center').valueString.getValue()"
            ),
            clinicalIdentifier=obj.fhirpath_single(
                "Patient.identifier.where(type.coding.code='MR').value.getValue()"
            ),
            consentStatus=cls.map_to_internal(
                "consentStatus",
                obj.fhirpath_single(
                    "Patient.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-cancer-patient-consent-status').valueCode.getValue()"
                ),
            ),
            vitalStatus=cls.map_to_internal(
                "vitalStatus",
                obj.fhirpath_single(
                    "Patient.deceasedDateTime.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-cancer-patient-vital-status').valueCodeableConcept.coding"
                ),
            ),
            gender=CodedConcept(
                code=obj.fhirpath_single("Patient.gender.getValue()"),
                system=cls._get_gender_codesystem(),
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
            sexAtBirth=(
                CodedConcept(
                    code=code,
                    system=cls._get_birthsex_codesystem(),
                )
                if (
                    code := obj.fhirpath_single(
                        "Patient.extension('http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex').valueCode.getValue()"
                    )
                )
                else None
            ),
            dateOfBirth=obj.fhirpath_single("Patient.birthDate.getValue()"),
            endOfRecords=obj.fhirpath_single(
                "Patient.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-cancer-patient-end-of-records').valueDate.getValue()"
            ),
            dateOfDeath=obj.fhirpath_single("Patient.deceasedDateTime.getValue()"),
            causeOfDeath=(
                CodedConcept.model_validate(coding.model_dump())
                if (
                    coding := obj.fhirpath_single(
                        "Patient.deceasedDateTime.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-cancer-patient-cause-of-death').valueCodeableConcept.coding"
                    )
                )
                else None
            ),
            genderIdentity=None,
        )

    @classmethod
    def onconova_to_fhir(cls, obj: schemas.PatientCase) -> fhir.OnconovaCancerPatient:
        resource = fhir.OnconovaCancerPatient.model_construct()
        resource.id = str(obj.id)
        resource.text = Narrative(
            status="generated",
            div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
        )
        resource.identifier = [
            fhir.OnconovaCancerPatientOnconovaIdentifier(value=obj.pseudoidentifier),
            fhir.OnconovaCancerPatientClinicalIdentifier(
                value=obj.clinicalIdentifier,
                system=obj.clinicalCenter.replace(" ", "-"),
            ),
        ]
        resource.gender = obj.gender.code
        resource.birthDate = fhir.OnconovaCancerPatientBirthDate(
            value=obj.dateOfBirth,
            extension=[
                ext
                for ext in [
                    (
                        fhir.CancerPatientAge(valueInteger=int(obj.age))
                        if obj.age is not None
                        else None
                    ),
                    (
                        fhir.CancerPatientAgeAtDiagnosis(
                            valueInteger=int(obj.ageAtDiagnosis)
                        )
                        if obj.ageAtDiagnosis is not None
                        else None
                    ),
                ]
                if ext is not None
            ],
        )
        resource.deceasedDateTime = fhir.OnconovaCancerPatientDeceasedDateTime(
            value=obj.dateOfDeath,
            extension=[
                ext
                for ext in [
                    fhir.OnconovaCancerPatientVitalStatus(
                        valueCodeableConcept=fhir.CodeableConcept(
                            coding=[cls.map_to_fhir("vitalStatus", obj.vitalStatus)]
                        )
                    ),
                    (
                        fhir.OnconovaCancerPatientCauseOfDeath(
                            valueCodeableConcept=construct_fhir_codeable_concept(
                                obj.causeOfDeath
                            )
                        )
                        if obj.causeOfDeath
                        else None
                    ),
                ]
                if ext is not None
            ],
        )
        resource.extension = [
            fhir.CancerPatientClinicalCenter(valueString=obj.clinicalCenter)
        ]
        if obj.endOfRecords is not None:
            resource.extension.append(
                fhir.CancerPatientEndOfRecords(valueDate=obj.endOfRecords)
            )
        if obj.sexAtBirth is not None:
            resource.extension.append(
                fhir.USCoreBirthSexExtension(valueCode=obj.sexAtBirth.code)
            )
        if obj.genderIdentity is not None:
            resource.extension.append(
                fhir.USCoreGenderIdentityExtension(
                    valueCodeableConcept=construct_fhir_codeable_concept(
                        obj.genderIdentity
                    )
                )
            )

        if obj.dataCompletionRate is not None:
            resource.extension.append(
                fhir.CancerPatientDataCompletionRate(
                    valueDecimal=obj.dataCompletionRate
                )
            )
        if obj.contributors is not None and len(obj.contributors) > 0:
            resource.extension.extend(
                [
                    fhir.CancerPatientDataContributors(
                        valueReference=Reference(type="Person", display=contributor)
                    )
                    for contributor in obj.contributors
                ]
            )
        if obj.consentStatus is not None:
            resource.extension.append(
                fhir.CancerPatientConsentStatus(
                    valueCode=cls.map_to_fhir("consentStatus", obj.consentStatus)
                )
            )

        if obj.overallSurvival is not None:
            resource.extension.append(
                fhir.CancerPatientOverallSurvival(
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
                                coding=[fhir.Coding(**obj.race.model_dump())]
                            )
                        )
                    ]
                )
            )
        return resource


CancerPatientProfile.register_mapping(
    "vitalStatus",
    [
        MappingRule(
            PatientCaseVitalStatusChoices.ALIVE,
            fhir.Coding(
                code="438949009",
                system="http://snomed.info/sct",
                display="Alive",
            ),
        ),
        MappingRule(
            PatientCaseVitalStatusChoices.DECEASED,
            fhir.Coding(
                code="419099009",
                system="http://snomed.info/sct",
                display="Deceased",
            ),
        ),
        MappingRule(
            PatientCaseVitalStatusChoices.UNKNOWN,
            fhir.Coding(
                code="261665006",
                system="http://snomed.info/sct",
                display="Unknown",
            ),
        ),
        MappingRule(
            None,
            fhir.Coding(
                code="261665006",
                system="http://snomed.info/sct",
                display="Unknown",
            ),
        ),
    ],
)

# Consent status mappings
CancerPatientProfile.register_mapping(
    "consentStatus",
    [
        MappingRule(PatientCaseConsentStatusChoices.VALID, "valid", "Valid consent"),
        MappingRule(
            PatientCaseConsentStatusChoices.REVOKED,
            "revoked",
            "Revoked consent",
        ),
        MappingRule(
            PatientCaseConsentStatusChoices.UNKNOWN,
            "unknown",
            "Unknown consent status",
        ),
    ],
)
