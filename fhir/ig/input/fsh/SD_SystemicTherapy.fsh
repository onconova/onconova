Profile: OnconovaMedicationAdministration
Parent: CancerRelatedMedicationAdministration
Id: onconova-systemic-therapy
Title: "Systemic Therapy Profile"
Description: "A profile representing a systemic therapy (e.g., chemotherapy, immunotherapy) administered to a cancer patient, including details about the medication, dosage, and administration schedule. This profile extends the base mCODE CancerRelatedMedicationAdministration profile to include specific constraints and requirements for Onconova."    
* subject only Reference(OnconovaCancerPatient)

* extension contains CombinedWith named combinedWith 0..*
* extension[combinedWith] ^short = "Other medication administered in combination"

* extension contains Cycles named cycles 0..1
* extension[cycles] ^short = "Total number of cycles for this medication"

* extension contains TherapyLineReference named therapyLine 0..1 
* extension[therapyLine] ^short = "Reference to the therapy line associated with this treatment"

* extension contains AdjunctiveRole named adjunctiveRole 0..1 
* extension[adjunctiveRole] ^short = "Role of this medication in the overall treatment plan"

* extension contains IsPrimaryTherapy named isPrimaryTherapy 0..1 
* extension[isPrimaryTherapy] ^short = "Indicates if this medication is the primary therapy within a therapy line"

* statusReason from TreatmentTerminationReasons

* medicationCodeableConcept from AntineoplasticAgents (required)

* reasonReference only Reference(OnconovaPrimaryCancerCondition or OnconovaSecondaryCancerCondition)


* insert NotUsed(reasonCode)
* insert NotUsed(context)
* insert NotUsed(supportingInformation)
* insert NotUsed(performer)
* insert NotUsed(request)

* effective[x] only Period



Extension: CombinedWith
Id: onconova-ext-combined-with
Title: "Combined With"
Description: "Indicates that this medication administration was given in combination with another medication administration."
* value[x] only Reference

Extension: Cycles
Id: onconova-ext-cycles
Title: "Cycles"
Description: "Indicates the total number of cycles for this medication administration."
* value[x] only integer

Extension: AdjunctiveRole
Id: onconova-ext-adjunctive-role
Title: "Adjunctive Role"
Description: "Indicates the role of this medication administration in the context of the overall treatment plan."
* value[x] only CodeableConcept
* valueCodeableConcept from AdjunctiveTherapyRoles (required)


Extension: IsPrimaryTherapy
Id: onconova-ext-is-primary-therapy
Title: "Is Primary Therapy"
Description: "Indicates whether this medication administration is the primary therapy within a therapy line."
* value[x] only boolean
