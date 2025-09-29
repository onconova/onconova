Profile: OnconovaSurgicalProcedure
Parent: CancerRelatedSurgicalProcedure
Id: onconova-surgical-procedure
Title: "Surgical Procedure Profile"
Description: """
A profile representing a surgical procedure performed on a cancer patient, including details about the procedure, its intent, and relevant dates. 

It extends the base mCODE [CancerRelatedSurgicalProcedure profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-cancer-related-surgical-procedure) to include specific constraints and requirements for Onconova.
"""
* status = #completed 
* subject only Reference(OnconovaCancerPatient)
* reasonReference only Reference(OnconovaPrimaryCancerCondition or OnconovaSecondaryCancerCondition)

// Add extension for referencing the therapy line
* extension contains TherapyLineReference named therapyLine 0..1 
* extension[therapyLine] ^short = "Reference to the therapy line associated with this treatment"

// Annotate unused elements
* insert NotUsed(basedOn)
* insert NotUsed(partOf)
* insert NotUsed(statusReason)
* insert NotUsed(encounter)
* insert NotUsed(recorder)
* insert NotUsed(asserter)
* insert NotUsed(performer)
* insert NotUsed(location)
* insert NotUsed(reasonCode)
* insert NotUsed(report)
* insert NotUsed(complication)
* insert NotUsed(complicationDetail)
* insert NotUsed(followUp)
* insert NotUsed(focalDevice)
* insert NotUsed(usedReference)
* insert NotUsed(usedCode)