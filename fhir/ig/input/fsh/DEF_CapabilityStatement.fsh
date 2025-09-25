Alias: $RefPolicy = http://hl7.org/fhir/reference-handling-policy

Instance: onconova-capability-statement
InstanceOf: CapabilityStatement
Usage: #definition
* description = "Retrieves a Bundle of Condition resources with a code in mCODE's cancer condition value set, and allows for associated Patient resources to be retrieved in a subsequent request. Use ONLY when reverse chaining AND `_include` are not available on the system."
* name = "OnconovaCapabilityStatement"
* title = "Onconova Capability Statement"
* format[0] = #json
* format[1] = #xml
* fhirVersion = #4.0.1
* status = #draft
* date = "2025-09-25"
* kind = #capability
* implementationGuide = Canonical(onconova.fhir)
* rest[0].mode = #server
* rest.documentation =  "An mCODE Server **SHALL**:\n\n1. Support all profiles defined in this Implementation Guide..\n1.  Implement the RESTful behavior according to the FHIR specification.\n1. Return the following response classes:\n   - (Status 400): invalid parameter\n   - (Status 401/4xx): unauthorized request\n   - (Status 403): insufficient scope\n   - (Status 404): unknown resource\n   - (Status 410): deleted resource.\n1. Support json source formats for all mCODE interactions.\n1. Identify the mCODE  profiles supported as part of the FHIR `meta.profile` attribute for each instance.\n1. Support the searchParameters on each profile individually and in combination.\n\nThe mCODE Server **SHOULD**:\n\n1. Support xml source formats for all mCODE interactions.\n"
* rest.security.description = "1. See the [General Security Considerations](https://www.hl7.org/fhir/security.html#general) section for requirements and recommendations.\n1. A server **SHALL** reject any unauthorized requests by returning an `HTTP 401` unauthorized response code."
* imports = "http://hl7.org/fhir/us/mcode/CapabilityStatement/mcode-sender-patient-bundle" 


// GET [base]/$mcode-patient-bundle/[id]
* rest[=].operation[+].name = "mcode-patient-bundle"
* rest[=].operation[=].definition = "http://hl7.org/fhir/us/mcode/OperationDefinition/mcode-patient-everything"
* rest[=].operation[=].extension.url = "http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation"
* rest[=].operation[=].extension.valueCode = #SHALL

// VERB [base]/Patient/[id]
* insert ResourceCRUD(Patient)
* rest[=].resource[=].profile = Canonical(OnconovaCancerPatient)

// VERB [base]/Condition/[id]
* insert ResourceCRUD(Condition)
* insert ResourceSupportedProfile(OnconovaPrimaryCancerCondition)
* insert ResourceSupportedProfile(OnconovaSecondaryCancerCondition)

// VERB [base]/Observation/[id]
* insert ResourceCRUD(Observation)
* insert ResourceSupportedProfile(OnconovaTumorMarker)
* insert ResourceSupportedProfile(OnconovaCancerRiskAssessment)
* insert ResourceSupportedProfile(OnconovaGenomicVariant)
* insert ResourceSupportedProfile(OnconovaTumorMutationalBurden)
* insert ResourceSupportedProfile(OnconovaMicrosatelliteInstability)
* insert ResourceSupportedProfile(OnconovaLossOfHeterozygosity)
* insert ResourceSupportedProfile(OnconovaHomologousRecombinationDeficiency)
* insert ResourceSupportedProfile(OnconovaTumorNeoantigenBurden)
* insert ResourceSupportedProfile(OnconovaAneuploidScore)
* insert ResourceSupportedProfile(OnconovaCancerStage)
* insert ResourceSupportedProfile(OnconovaTNMStageGroup)
* insert ResourceSupportedProfile(OnconovaComorbidities)
* insert ResourceSupportedProfile(OnconovaLifestyle)
* insert ResourceSupportedProfile(OnconovaKarnofskyPerformanceStatus)
* insert ResourceSupportedProfile(OnconovaECOGPerformanceStatus)
* insert ResourceSupportedProfile(OnconovaImagingDiseaseStatus)
* insert ResourceSupportedProfile(OnconovaTNMPrimaryTumorCategory)
* insert ResourceSupportedProfile(OnconovaTNMDistantMetastasesCategory)
* insert ResourceSupportedProfile(OnconovaTNMRegionalNodesCategory)
* insert ResourceSupportedProfile(OnconovaTNMLymphaticInvasionCategory)
* insert ResourceSupportedProfile(OnconovaTNMPerineuralInvasionCategory)
* insert ResourceSupportedProfile(OnconovaTNMResidualTumorCategory)
* insert ResourceSupportedProfile(OnconovaTNMGradeCategory)
* insert ResourceSupportedProfile(OnconovaTNMSerumTumorMarkerLevelCategory)
* insert ResourceSupportedProfile(OnconovaTNMVenousInvasionCategory)
* insert ResourceSupportedProfile(http://hl7.org/fhir/StructureDefinition/bodyheight)
* insert ResourceSupportedProfile(http://hl7.org/fhir/StructureDefinition/bodyweight)
* insert ResourceSupportedProfile(http://hl7.org/fhir/StructureDefinition/bodytemp)
* insert ResourceSupportedProfile(http://hl7.org/fhir/StructureDefinition/bmi)
* insert ResourceSupportedProfile(http://hl7.org/fhir/StructureDefinition/bp)

// VERB [base]/Procedure/[id]
* insert ResourceCRUD(Procedure)
* insert ResourceSupportedProfile(OnconovaSurgicalProcedure)
* insert ResourceSupportedProfile(OnconovaRadiotherapySummary)
* insert ResourceSupportedProfile(OnconovaTumorBoardReview)
* insert ResourceSupportedProfile(OnconovaMolecularTumorBoardReview)

// VERB [base]/MedicationAdministration/[id]
* insert ResourceCRUD(MedicationAdministration)
* insert ResourceSupportedProfile(OnconovaMedicationAdministration)

// VERB [base]/FamilyHistory/[id]
* insert ResourceCRUD(FamilyHistory)
* insert ResourceSupportedProfile(OnconovaCancerFamilyMemberHistory)

// VERB [base]/List/[id]
* rest[=].resource[+].type = #List
* rest[=].resource[=].referencePolicy[+] = $RefPolicy#literal
* rest[=].resource[=].interaction[+].code = #read
* insert ResourceSupportedProfile(OnconovaTherapyLine)