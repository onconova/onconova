Profile: OnconovaPrimaryCancerCondition
Id: onconova-primary-cancer-condition
Title: "Primary Cancer Condition Profile"
Parent: PrimaryCancerCondition
Description: """
A profile that records the primary cancer condition, the original or first neoplasm in the body (Definition from: [NCI Dictionary of Cancer Terms](https://www.cancer.gov/publications/dictionaries/cancer-terms/def/primary-tumor)). Cancers that are not clearly secondary (i.e., of uncertain origin or behavior) should be documented as primary.

It constrains the mCODE [PrimaryCancerCCondition profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-primary-cancer-condition) to constrain the terminologies of the cancer topography and morphology extensions to use exclusively ICD-O-3 codes.
"""
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#363346000 "Malignant neoplastic disease"

// Constratin the cancer morphology extension to use ICD-O-3 codes and be required
* extension[histologyMorphologyBehavior] 1..1
* extension[histologyMorphologyBehavior].valueCodeableConcept from ICDO3MorphologyBehavior (required)

// Constratin the cancer topography to use ICD-O-3 codes and be required 
* bodySite 1..*
* bodySite from ICDO3Topography (required)

// Add extension to indicate whether the condition is a recurrence of a previous condition
* extension contains RecurrenceOf named recurrenceOf 0..1 

// Annotate unused elements to indicate they are not supported in this profile
* insert NotUsed(stage)
* insert NotUsed(evidence)
* insert NotUsed(recorder)
* insert NotUsed(asserter)
* insert NotUsed(verificationStatus)
* insert NotUsed(recordedDate)
* insert NotUsed(encounter)
* insert NotUsed(severity)



Profile: OnconovaSecondaryCancerCondition
Parent: SecondaryCancerCondition
Id: onconova-secondary-cancer-condition
Title: "Secondary Cancer Condition Profile"
Description: """
A profile recording the a secondary neoplasm, including location and the date of onset of metastases. A secondary cancer results from the spread (metastasization) of cancer from its original site (Definition from: NCI Dictionary of Cancer Terms).

It constrains the mCODE [SecondaryCancerCCondition profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-secondary-cancer-condition) to constrain the terminologies of the cancer topography and morphology extensions to use exclusively ICD-O-3 codes.
"""
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#128462008 "Secondary malignant neoplastic disease"
* extension[relatedPrimaryCancerCondition].valueReference only Reference(OnconovaPrimaryCancerCondition) 

// Constratin the cancer morphology extension to use ICD-O-3 codes and be required
* extension[histologyMorphologyBehavior] 1..1
* extension[histologyMorphologyBehavior].valueCodeableConcept from ICDO3MorphologyBehavior (required)

// Constratin the cancer topography to use ICD-O-3 codes and be required 
* bodySite 1..*
* bodySite from ICDO3Topography (required)

// Annotate unused elements to indicate they are not supported in this profile
* insert NotUsed(stage)
* insert NotUsed(evidence)
* insert NotUsed(recorder)
* insert NotUsed(asserter)
* insert NotUsed(verificationStatus)
* insert NotUsed(recordedDate)
* insert NotUsed(encounter)
* insert NotUsed(severity)

// ================ 
// Extensions
// ================

Extension: RecurrenceOf
Id: onconova-ext-recurrence-of
Title: "Recurrence Of"
Description: "Indicates that the condition is a recurrence of a previous condition, and provides a reference to that previous condition."
* value[x] only Reference(PrimaryCancerCondition)
* obeys recurrence-reference 

Invariant: recurrence-reference
Description: "If the Condition.clinicalStatus extension is 'recurrence', the recurrenceOf extension must be present."
Expression: "%resource.clinicalStatus.exists() and %resource.clinicalStatus = 'recurrence' implies exists() valueReference.exists()"
Severity: #error