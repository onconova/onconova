from fhircraft.fhir.resources.datatypes.R4.complex import (
    Duration,
    Reference,
)
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
                "Patient.identifier.where(type.coding.code='MR').system"
            ),
            clinicalIdentifier=obj.fhirpath_single(
                "Patient.identifier.where(type.coding.code='MR').value"
            ),
            consentStatus=cls.map_to_internal(
                "consentStatus",
                obj.fhirpath_single(
                    "Patient.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-consent-status').valueCode"
                ),
            ),
            vitalStatus=cls.map_to_internal(
                "vitalStatus",
                obj.fhirpath_single(
                    "Patient.deceasedDateTime.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-vital-status').valueCodeableConcept.coding"
                ),
            ),
            gender=CodedConcept(
                code=obj.fhirpath_single("Patient.gender"),
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
            sexAtBirth=CodedConcept(
                code=obj.fhirpath_single(
                    "Patient.extension('http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex').valueCode"
                ),
                system=cls._get_birthsex_codesystem(),
            ),
            dateOfBirth=obj.fhirpath_single("Patient.birthDate.getValue()"),
            endOfRecords=obj.fhirpath_single(
                "Patient.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-end-of-records').valueDate"
            ),
            dateOfDeath=obj.fhirpath_single("Patient.deceasedDateTime.getValue()"),
            causeOfDeath=(
                CodedConcept.model_validate(coding)
                if (
                    coding := obj.fhirpath_single(
                        "Patient.deceasedDateTime.extension('http://onconova.github.io/fhir/StructureDefinition/onconova-ext-cause-of-death').valueCodeableConcept.coding"
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
            text=fhir.Narrative(
                status="generated",
                div=f'<div xmlns="http://www.w3.org/1999/xhtml">{obj.description}</div>',
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
                    valueCodeableConcept=fhir.CodeableConcept(
                        coding=[fhir.Coding(**obj.genderIdentity.model_dump())]
                    )
                )
            )
        resource.birthDate_ext = fhir.Element()
        resource.birthDate_ext.extension = []
        if obj.age is not None:
            resource.birthDate_ext.extension.append(
                fhir.AgeExtension(valueInteger=obj.age)
            )
        if obj.ageAtDiagnosis is not None:
            resource.birthDate_ext.extension.append(
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
                    valueCode=cls.map_to_fhir("consentStatus", obj.consentStatus)
                )
            )
        resource.deceasedDateTime_ext = fhir.Element()
        resource.deceasedDateTime_ext.extension = []
        if obj.vitalStatus is not None:
            resource.deceasedDateTime_ext.extension.append(
                fhir.VitalStatus(
                    valueCodeableConcept=fhir.CodeableConcept(
                        coding=[cls.map_to_fhir("vitalStatus", obj.vitalStatus)]
                    )
                )
            )
        if obj.causeOfDeath is not None:
            resource.deceasedDateTime_ext.extension.append(
                fhir.CauseOfDeath(
                    valueCodeableConcept=fhir.CodeableConcept(
                        coding=[fhir.Coding(**obj.causeOfDeath.model_dump())]
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
                                coding=[fhir.Coding(**obj.race.model_dump())]
                            )
                        )
                    ]
                )
            )
        assert resource.meta is not None
        resource.meta.lastUpdated = obj.updatedAt
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
