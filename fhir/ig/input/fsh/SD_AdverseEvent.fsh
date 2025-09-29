Profile: OnconovaAdverseEvent
Parent: AdverseEvent
Id: onconova-adverse-event
Title: "Adverse Event Profile"
Description: """
A profile representing an adverse event experienced by a cancer patient as a result of an antineoplastic treatment, structured according to the Common Terminology Criteria for Adverse Events (CTCAE). This resource is used to capture and standardize the documentation of adverse events occurring during cancer care, including the type of event, its CTCAE grade, and any mitigation actions taken.

The profile constrains the base FHIR `AdverseEvent` resource to ensure consistent use of CTCAE codes and grades, and supports linkage to related treatments such as medications, radiotherapy, or surgical procedures documented in Onconova. The profile also provides extensions for recording mitigation strategies, supporting detailed tracking and management of adverse events in cancer patients.
"""
// Reference Onconova resources
* subject only Reference(OnconovaCancerPatient)
* suspectEntity.instance only Reference(OnconovaMedicationAdministration or OnconovaRadiotherapySummary or OnconovaSurgicalProcedure)

// Only actual events are recorded
* actuality = #actual 

// Use CTCAE codes for the event
* event from CTCAdverseEvents (required)

// Add CTCAE grade extension
* extension contains CTCGrade named ctcGrade 1..1 
* extension[ctcGrade] ^short = "CTCAE Grade"

// Add mitigation actions extension
* extension contains AdverseEventMitigation named adverseEventMitigation 0..* // Mitigation actions taken
* extension[adverseEventMitigation] ^short = "Adverse Event Mitigation Action(s)"

// Annotate unused elements for this profile
* insert NotUsed(category)
* insert NotUsed(encounter)
* insert NotUsed(detected)
* insert NotUsed(recordedDate)
* insert NotUsed(resultingCondition)
* insert NotUsed(location)
* insert NotUsed(seriousness)
* insert NotUsed(severity)
* insert NotUsed(recorder)
* insert NotUsed(contributor)

// ============================
// Extensions Definitions
// ============================

Extension: CTCGrade
Id: onconova-ext-ctc-grade
Title: "CTCAE Grade"
Context: AdverseEvent
Description: "The grade of the adverse event as defined by the Common Terminology Criteria for Adverse Events (CTCAE)."
* value[x] only integer
* valueInteger ^short = "CTCAE Grade"
* valueInteger ^definition = "The CTCAE grade must be an integer between 1 and 5, inclusive."
* obeys ctcae-grade

Invariant: ctcae-grade
Description: "The CTCAE grade must be between 1 and 5, inclusive."
Expression: "valueInteger() >= 1 and valueInteger() <= 5"
Severity: #error

Extension: AdverseEventMitigation
Id: onconova-ext-adverse-event-mitigation
Title: "Adverse Event Mitigation"
Context: AdverseEvent
Description: "Details about an action taken to mitigate or manage the adverse event."
* value[x] 0..0
* extension contains 
    category 1..1 and 
    adjustment 0..1 and
    drug 0..1 and
    procedure 0..1 and
    management 0..1 

* obeys drug-mitigation and adjustment-mitigation and procedural-mitigation

* extension[category].value[x] only CodeableConcept
* extension[category].valueCodeableConcept from AdverseEventMitigationCategories (required)
* extension[category] ^short = "Mitigation Category"
* extension[category] ^definition = "Type of mitigation action taken to address the adverse event."

* extension[adjustment].value[x] only CodeableConcept
* extension[adjustment].valueCodeableConcept from AdverseEventMitigationTreatmentAdjustments (required)
* extension[adjustment] ^short = "Treatment Adjustment"
* extension[adjustment] ^definition = "Details of any adjustments made to the treatment regimen in response to the adverse event."

* extension[drug].value[x] only CodeableConcept
* extension[drug].valueCodeableConcept from AdverseEventMitigationDrugs (required)
* extension[drug] ^short = "Mitigation Drug"
* extension[drug] ^definition = "Medication administered to mitigate the adverse event."

* extension[procedure].value[x] only CodeableConcept
* extension[procedure].valueCodeableConcept from AdverseEventMitigationProcedures (required)
* extension[procedure] ^short = "Mitigation Procedure"
* extension[procedure] ^definition = "Procedure performed to mitigate the adverse event."

* extension[management].value[x] only CodeableConcept
* extension[management].valueCodeableConcept from AdverseEventMitigationManagements (required)
* extension[management] ^short = "Management"
* extension[management] ^definition = "Management strategies employed to address the adverse event."

Invariant: drug-mitigation
Description: "If the mitigation category is 'Drug', then only mitigation drug must be specified."
Expression: "extension('category').valueCodeableConcept.coding.code = 'C49158' implies (extension('drug').exists() and not extension('procedure').exists() and not extension('adjustment').exists())"
Severity: #error

Invariant: adjustment-mitigation
Description: "If the mitigation category is 'Adjustment', then only mitigation adjustment must be specified."
Expression: "extension('category').valueCodeableConcept.coding.code = 'C49157' implies (extension('adjustment').exists() and not extension('procedure').exists() and not extension('drug').exists())"
Severity: #error

Invariant: procedural-mitigation
Description: "If the mitigation category is 'Procedure', then only mitigation procedure must be specified."
Expression: "extension('category').valueCodeableConcept.coding.code = 'C49159' implies (extension('procedure').exists() and not extension('adjustment').exists() and not extension('drug').exists())"
Severity: #error

