Profile: OnconovaRadiotherapySummary
Parent: RadiotherapyCourseSummary
Id: onconova-radiotherapy-summary
Title: "Radiotherapy Summary Profile"
Description: "A profile representing a summary of a radiotherapy course for a cancer patient, including details about the treatment intent, modality, and relevant dates. This profile extends the base mCODE RadiotherapyCourseSummary profile to include specific constraints and requirements for Onconova."
* subject only Reference(OnconovaCancerPatient)

* extension contains TherapyLineReference named therapyLine 0..1 
* extension[therapyLine] ^short = "Reference to the therapy line associated with this treatment"

* statusReason from TreatmentTerminationReasons (required)