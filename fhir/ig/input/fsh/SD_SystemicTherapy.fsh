Profile: OnconovaMedicationAdministration
Parent: CancerRelatedMedicationAdministration
Id: onconova-medication-administration
Title: "Medication Administration Profile"
Description: """
A profile representing a medication administered to a cancer patient during a systemic therapy (e.g., chemotherapy, immunotherapy), including details about the medication and dosage. 

This profile extends the base mCODE [CancerRelatedMedicationAdministration profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-cancer-related-medication-administration) to introduce additional information about the systemic therapy (e.g. number of cycles, therapeutic role, etc.) and to introduce references to other medication administration given simultaneously to represent combination therapies."""    

// USe Onconova profile references
* subject only Reference(OnconovaCancerPatient)
* reasonReference only Reference(OnconovaPrimaryCancerCondition or OnconovaSecondaryCancerCondition)

// Constrain the valuesets
* statusReason from TreatmentTerminationReasons (required)
* medicationCodeableConcept from AntineoplasticAgents (required)

// Only document administrations over a period of time
* effective[x] only Period

// Add extension to reference combined medications
* extension contains CombinedWith named combinedWith 0..*
* extension[combinedWith] ^short = "Other medication administered in combination"

// Add extension to document number of cycles over the administration period
* extension contains Cycles named cycles 0..1
* extension[cycles] ^short = "Total number of cycles for this medication"

// Add extension to reference the therapy line
* extension contains TherapyLineReference named therapyLine 0..1 
* extension[therapyLine] ^short = "Reference to the therapy line associated with this treatment"

// Add extensions to document the therapeutic role of the administration
* extension contains AdjunctiveRole named adjunctiveRole 0..1 
* extension[adjunctiveRole] ^short = "Role of this medication in the overall treatment plan"
* extension contains IsPrimaryTherapy named isPrimaryTherapy 0..1 
* extension[isPrimaryTherapy] ^short = "Indicates if this medication is the primary therapy within a therapy line"

// Annotate unused elements
* insert NotUsed(reasonCode)
* insert NotUsed(context)
* insert NotUsed(supportingInformation)
* insert NotUsed(performer)
* insert NotUsed(request)
* insert NotUsed(partOf)
* insert NotUsed(reasonCode)


//================
// Extension
//================

Extension: CombinedWith
Id: onconova-ext-combined-with
Title: "Combined With"
Description: "Indicates that this medication administration was given in combination with another medication administration."
* value[x] only Reference(OnconovaMedicationAdministration)

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
