Profile: OnconovaSurgicalProcedure
Parent: CancerRelatedSurgicalProcedure
Id: onconova-surgical-procedure
Title: "Surgical Procedure Profile"
Description: "A profile representing a surgical procedure performed on a cancer patient, including details about the procedure, its intent, and relevant dates. This profile extends the base mCODE CancerRelatedSurgicalProcedure profile to include specific constraints and requirements for Onconova."
* subject only Reference(OnconovaCancerPatient)

* extension contains TherapyLineReference named therapyLine 0..1 
* extension[therapyLine] ^short = "Reference to the therapy line associated with this treatment"
