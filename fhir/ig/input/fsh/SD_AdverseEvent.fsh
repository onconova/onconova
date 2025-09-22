Profile: OnconovaAdverseEvent
Parent: AdverseEvent
Id: onconova-adverse-event
Title: "Onconova Adverse Event Profile"
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
* extension contains AdverseEventMitigationCategory named category 1..1 // Category of mitigation action
* extension contains AdverseEventMitigationAdjustment named adjustment 0..1 // Treatment adjustments
* extension contains AdverseEventMitigationDrug named drug 0..1 // Drugs used for mitigation
* extension contains AdverseEventMitigationProcedure named procedure 0..1 // Procedures used for mitigation
* extension contains AdverseEventMitigationManagement named management 0..1 // Overall management strategies

Extension: AdverseEventMitigationCategory
Id: onconova-ext-adverse-event-mitigation-category
Title: "Adverse Event Mitigation Category"
Description: "The category of mitigation or management action taken for the adverse event."
* value[x] only CodeableConcept
* valueCodeableConcept from AdverseEventMitigationCategories (required)


Extension: AdverseEventMitigationAdjustment
Id: onconova-ext-adverse-event-mitigation-adjustment
Title: "Adverse Event Mitigation Adjustment"
Description: "Details about any adjustments made to the treatment regimen as a result of the adverse event."
* value[x] only CodeableConcept
* valueCodeableConcept from AdverseEventMitigationTreatmentAdjustments (required)

Extension: AdverseEventMitigationDrug
Id: onconova-ext-adverse-event-mitigation-drug
Title: "Adverse Event Mitigation Drug"
Description: "Details about any drugs used to mitigate the adverse event."
* value[x] only CodeableConcept
* valueCodeableConcept from AdverseEventMitigationDrugs (required)

Extension: AdverseEventMitigationProcedure
Id: onconova-ext-adverse-event-mitigation-procedure
Title: "Adverse Event Mitigation Procedure"
Description: "Details about any procedures used to mitigate the adverse event."
* value[x] only CodeableConcept
* valueCodeableConcept from AdverseEventMitigationProcedures (required)

Extension: AdverseEventMitigationManagement
Id: onconova-ext-adverse-event-mitigation-management
Title: "Adverse Event Mitigation Management"
Description: "Details about the overall management strategies employed to mitigate the adverse event."
* value[x] only CodeableConcept
* valueCodeableConcept from AdverseEventMitigationManagements (required)