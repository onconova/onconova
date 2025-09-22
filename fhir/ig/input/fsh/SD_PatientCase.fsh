Profile: OnconovaCancerPatient
Parent: CancerPatient
Id: onconova-cancer-patient
Title: "Onconova Cancer Patient Profile"
Description: "A profile representing a cancer patient with specific extensions and constraints for the Onconova use case. Any Patient resource complying US Core Patient or mCODE CancerPatient profiles will also comply with Onconova CancerPatient."
// Security label for pseudonymized data
* meta.security = #PSEUDED

// Slicing identifier to allow for Onconova-specific pseudoidentifier
* identifier ^slicing.rules = #open // Allow additional identifiers
* identifier ^slicing.discriminator[0].type = #pattern // Slice by system value
* identifier ^slicing.discriminator[0].path = "system"
* identifier contains onconovaIdentifier 1..* // Require at least one Onconova identifier
* identifier[onconovaIdentifier] 1..* // Cardinality for the slice
* identifier[onconovaIdentifier].type.coding = http://terminology.hl7.org/CodeSystem/v2-0203#ACSN "Accession Identifier" // Coding for identifier type
* identifier[onconovaIdentifier].system = "Onconova" // System for Onconova pseudoidentifier
* identifier[onconovaIdentifier].value 1..1 MS // Value is required and must-support
* identifier[onconovaIdentifier] ^short = "Onconova Pseudoidentifier" // Short description for slice

// Only allow dateTime for deceased[x]
* deceased[x] only dateTime

// Add anonymized entry extension to name
* name.extension contains AnonymizedEntry named anonymizedEntry 1..* // Allow multiple anonymized entry extensions

// Add custom extensions for clinical data
* extension contains OverallSurvival named overallSurvival 0..1 // Overall survival duration
* extension contains Age named age 0..1 // Patient's age
* extension contains AgeAtDiagnosis named ageAtDiagnosis 0..1 // Age at diagnosis
* extension contains DataCompletionRate named dataCompletionRate 0..1 // Data completion rate
* extension contains Contributors named contributors 0..* // Contributors to care
* extension contains CauseOfDeath named causeOfDeath 0..1 // Cause of death
* extension contains EndOfRecords named endOfRecords 0..1 // End of records date

// Annotate unused elements for this profile
* insert NotUsed(telecom) // No telecom information
* insert NotUsed(address) // No address information
* insert NotUsed(contact) // No contact information
* insert NotUsed(maritalStatus) // No marital status
* insert NotUsed(communication) // No communication info
* insert NotUsed(photo) // No photo
* insert NotUsed(generalPractitioner) // No general practitioner

// Extension: OverallSurvival
// Captures the duration of time from diagnosis or treatment start that a patient is still alive
Extension: OverallSurvival
Id: onconova-ext-overall-survival
Title: "Overall Survival"
Description: "The duration of time from either the date of diagnosis or the start of treatment for a disease, such as cancer, that patients diagnosed with the disease are still alive. In a clinical trial, measuring the overall survival is one way to see how well a new treatment works."
* value[x] only decimal 

// Extension: Age
// Captures the approximate age of the patient
Extension: Age
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
* valueCodeableConcept from CausesOfDeathVS (required)
