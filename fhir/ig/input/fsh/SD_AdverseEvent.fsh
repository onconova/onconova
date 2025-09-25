Profile: OnconovaAdverseEvent
Parent: AdverseEvent
Id: onconova-adverse-event
Title: "Adverse Event Profile"
Description: "A profile representing an adverse event experienced by a cancer patient based on CTCAE, including details about the event, its severity, and related conditions. This profile extends the base FHIR AdverseEvent resource."
// Reference Onconova resources
* subject only Reference(OnconovaCancerPatient)
* suspectEntity.instance only Reference(OnconovaMedicationAdministration or OnconovaRadiotherapySummary or OnconovaSurgicalProcedure)



// Only actual events are recorded
* actuality = #actual 

// Use CTCAE codes for the event
* event from CTCAdverseEvents (required)

* extension contains CTCGrade named ctcGrade 1..1 // CTCAE grade extension
* extension[ctcGrade] ^short = "CTCAE Grade"

* extension contains AdverseEventMitigation named adverseEventMitigation 0..* // Mitigation actions taken
* extension[adverseEventMitigation] ^short = "Adverse Event Mitigations"

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

Extension: CTCGrade
Id: onconova-ext-ctc-grade
Title: "CTCAE Grade"
Description: "The grade of the adverse event as defined by the Common Terminology Criteria for Adverse Events (CTCAE)."
* value[x] only integer

Extension: AdverseEventMitigation
Id: onconova-ext-adverse-event-mitigation
Title: "Adverse Event Mitigation"
Description: "Details about the actions taken to mitigate or manage the adverse event."
* value[x] 0..0
* extension contains 
    category 1..1 and 
    adjustment 0..1 and
    drug 0..1 and
    procedure 0..1 and
    management 0..1 

* extension[category].value[x] only CodeableConcept
* extension[category].valueCodeableConcept from AdverseEventMitigationCategories (required)

* extension[adjustment].value[x] only CodeableConcept
* extension[adjustment].valueCodeableConcept from AdverseEventMitigationTreatmentAdjustments (required)

* extension[drug].value[x] only CodeableConcept
* extension[drug].valueCodeableConcept from AdverseEventMitigationDrugs (required)

* extension[procedure].value[x] only CodeableConcept
* extension[procedure].valueCodeableConcept from AdverseEventMitigationProcedures (required)

* extension[management].value[x] only CodeableConcept
* extension[management].valueCodeableConcept from AdverseEventMitigationManagements (required)