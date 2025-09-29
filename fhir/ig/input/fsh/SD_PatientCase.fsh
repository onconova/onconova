Profile: OnconovaCancerPatient
Parent: CancerPatient
Id: onconova-cancer-patient
Title: "Cancer Patient Profile"
Description: """
A profile representing a cancer patient with specific extensions and constraints for the Onconova use case. Due to the research-scope of Onconova, the patient information is anonymized and identifying data elements are not provided. 

It constrains the mCODE [CancerPatient profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-cancer-patient) to ensure anonymity of the patient information and to introduce additional Onconova-specific case information. Any `Patient` resource complying with the US Core `Patient` or mCODE `CancerPatient` profiles will also comply with this profile. 
"""
// Security label for pseudonymized data
* meta.security = #PSEUDED

// Slicing identifier to allow for Onconova-specific pseudoidentifier
* identifier ^slicing.rules = #open 
* identifier ^slicing.discriminator[0].type = #pattern 
* identifier ^slicing.discriminator[0].path = "system"

// Add slice to contain the Onconova case logical identifier
* identifier contains onconovaIdentifier 1..* 
* identifier[onconovaIdentifier] 1..* // Cardinality for the slice
* identifier[onconovaIdentifier].type = http://terminology.hl7.org/CodeSystem/v2-0203#ACSN "Accession Identifier" // Coding for identifier type
* identifier[onconovaIdentifier].system = "Onconova" // System for Onconova pseudoidentifier
* identifier[onconovaIdentifier].value 1..1 MS // Value is required and must-support
* identifier[onconovaIdentifier] ^short = "Onconova Pseudoidentifier" // Short description for slice

// Only allow dateTime for deceased[x]
* deceased[x] only dateTime

// Add anonymized entry extension to name
* name.extension contains AnonymizedEntry named anonymizedEntry 1..* // Allow multiple anonymized entry extensions

// Add custom extensions for clinical data
* extension contains
    OverallSurvival named overallSurvival 0..1 and
    AgeExtension named age 0..1 and
    AgeAtDiagnosis named ageAtDiagnosis 0..1 and
    DataCompletionRate named dataCompletionRate 0..1 and
    Contributors named contributors 0..* and
    CauseOfDeath named causeOfDeath 0..1 and 
    EndOfRecords named endOfRecords 0..1

// Annotate unused elements for this profile
* insert NotUsed(telecom) // No telecom information
* insert NotUsed(address) // No address information
* insert NotUsed(contact) // No contact information
* insert NotUsed(maritalStatus) // No marital status
* insert NotUsed(communication) // No communication info
* insert NotUsed(photo) // No photo
* insert NotUsed(generalPractitioner) // No general practitioner

//==================
// Extensions
//==================

Extension: AnonymizedEntry
Id: onconova-ext-anonymized-entry 
Title: "Anonymized Entry"
Description: "Value not provided to maintain the anonymization of the patient's data and conform to data protection regulations for research data."
* value[x] only code
* value[x] = #masked

Extension: UnknownEntry
Id: onconova-ext-unknown-entry
Title: "Unknown Entry"
Description: "Value is not collected and cannot be provided by Onconova."
* value[x] only code
* value[x] = #unknown

// Extension: OverallSurvival
// Captures the duration of time from diagnosis or treatment start that a patient is still alive
Extension: OverallSurvival
Id: onconova-ext-overall-survival
Title: "Overall Survival"
Description: "The duration of time from either the date of diagnosis or the start of treatment for a disease, such as cancer, that patients diagnosed with the disease are still alive. In a clinical trial, measuring the overall survival is one way to see how well a new treatment works."
* value[x] only decimal 

// Extension: Age
// Captures the approximate age of the patient
Extension: AgeExtension
Id: onconova-ext-age
Title: "Age"
Description: "The approximate age of the patient."
* value[x] only Range

// Extension: EndOfRecords
// Indicates the last known record date of a patient
Extension: EndOfRecords
Id: onconova-ext-end-of-records
Title: "End of Records"
Description: "Indicates the last known record date of a patient."
* value[x] only date


// Extension: AgeAtDiagnosis
// Captures the approximate age of the patient at diagnosis
Extension: AgeAtDiagnosis
Id: onconova-ext-age-at-diagnosis
Title: "Age at Diagnosis"
Description: "The approximate age of the patient at the time of diagnosis of the disease."
* value[x] only Range 

// Extension: DataCompletionRate
// Percentage of data elements completed for a patient
Extension: DataCompletionRate
Id: onconova-ext-data-completion-rate
Title: "Data Completion Rate"
Description: "The percentage of data elements categories that have been completed for a patient."
* value[x] only decimal

// Extension: Contributors
// Individuals or organizations that contributed to the patient's care
Extension: Contributors
Id: onconova-ext-contributors
Title: "Contributors"
Description: "The individuals or organizations that contributed to the patient's care."
* value[x] only Reference

// Extension: CauseOfDeath
// The cause of death for the patient, using a required value set
Extension: CauseOfDeath
Id: onconova-ext-cause-of-death
Title: "Cause of Death"
Description: "The cause of death for the patient."
* value[x] only CodeableConcept
* valueCodeableConcept from CausesOfDeath (required)
