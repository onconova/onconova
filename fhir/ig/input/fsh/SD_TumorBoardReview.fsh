Profile: OnconovaTumorBoardReview
Parent: Procedure
Id: onconova-tumor-board-review
Title: "Tumor Board Review"
Description: """A profile representing a tumor board review for a cancer patient.

This profile extends the base FHIR `Procedure` resource since there is no equivalent mCODE profile that covers the use case. """    

// Basic constraints
* status = #completed
* category = $SNOMED#103693007 "Diagnostic procedure"
* subject only Reference(OnconovaCancerPatient)
* reasonReference only Reference(OnconovaPrimaryCancerCondition or OnconovaSecondaryCancerCondition)
* performed[x] only dateTime

// Set the type of procedure and extend the code for specializations
* code = $NCIT#C93304 "Tumor Board Review"
* code.extension contains TumorBoardSpecialization named specialization 0..1 MS 
* code.extension[specialization] ^short = "Tumor Board Specialization, if relevant"

// Profile the follow-up recommendations from the board
* followUp MS 
* followUp from OnconovaTumorBoardRecommendations (required)
* followUp ^short = "Tumor Board Recommendation"
* followUp ^definition = "Any recommendations or follow-up actions resulting from the tumor board."

//Annotate unused inherited elements
* insert NotUsed(location) 
* insert NotUsed(performer)
* insert NotUsed(asserter) 
* insert NotUsed(recorder)
* insert NotUsed(basedOn) 
* insert NotUsed(bodySite) 
* insert NotUsed(outcome) 
* insert NotUsed(complication) 
* insert NotUsed(complicationDetail) 
* insert NotUsed(reasonCode)


Profile: OnconovaMolecularTumorBoardReview
Parent: OnconovaTumorBoardReview
Id: onconova-molecular-tumor-board-review
Title: "Molecular Tumor Board Review"
Description: """
A profile representing a specialized molecular tumor board review for a cancer patient. This profile extends the `OnconovaTumorBoardReview` profile to specify that the review is focused on molecular diagnostics and recommendations.
"""

* code.extension[specialization].valueCodeableConcept = $NCIT#C20826 "Molecular Diagnosis"

// Add extensions for detailed therapeutic recommendations
* extension contains MolecularTumorBoardTherapeuticRecommendation named therapeuticRecommendation 0..* MS 
* extension ^short = "Therapeutic recommendation(s)"

// Add extensions for molecular comparison
* extension contains MolecularTumorBoardMolecularComparison named molecularComparison 0..1 MS
* extension ^short = "Molecular comparison(s)"

// Add extensions for CUP characterization
* extension contains MolecularTumorBoardCUPCharacterization named cupCharacterization 0..1 MS
* extension ^short = "CUP characterization(s)"


Extension: TumorBoardSpecialization
Id: onconova-ext-tumor-board-specialization
Title: "Tumor Board Specialization"
Description: "The specialization or focus area of the tumor board conducting the review, such as hematologic malignancies or solid tumors."
* value[x] only CodeableConcept


//==================
// Extensions 
//==================

Extension: MolecularTumorBoardTherapeuticRecommendation
Id: onconova-ext-molecular-tumor-board-therapeutic-recommendation
Title: "Molecular Tumor Board Therapeutic Recommendation"
Description: "A therapeutic recommendation or follow-up action resulting from a molecular tumor board review."

// Extensions for detailed recommendation information
* extension contains
    clinicalTrial 0..1 MS and
    medication 0..* MS and
    supportingEvidence 0..* MS and
    expectedEffect 0..1 MS and
    offLabelUse 0..1 MS and
    withinSoc 0..1 MS

// Type and binding for each extension
* extension[clinicalTrial].value[x] only string 
* extension[medication].value[x] only CodeableConcept
* extension[medication].valueCodeableConcept from AntineoplasticAgents (required)
* extension[supportingEvidence].value[x] only Reference(
    OnconovaTumorMarker or 
    OnconovaGenomicVariant or 
    OnconovaTumorMutationalBurden or 
    OnconovaMicrosatelliteInstability or 
    OnconovaLossOfHeterozygosity or 
    OnconovaHomologousRecombinationDeficiency or 
    OnconovaTumorNeoantigenBurden or
    OnconovaAneuploidScore
)
* extension[expectedEffect].value[x] only CodeableConcept
* extension[expectedEffect].valueCodeableConcept from ExpectedDrugEffects (required)
* extension[offLabelUse].value[x] only boolean
* extension[withinSoc].value[x] only boolean

// Invariants
* obeys tumor-board-therapeutic-recommendation-1

Invariant: tumor-board-therapeutic-recommendation-1
Description: "Either clinical trial or medication SHALL be present"
Expression: "extension('clinicalTrial').exists() or extension('medication').exists()"
Severity: #error


Extension: MolecularTumorBoardMolecularComparison
Id: onconova-ext-molecular-tumor-board-molecular-comparison
Title: "Molecular Tumor Board Molecular Comparison"
Description: "A comparison of molecular findings discussed during the molecular tumor board review."

// Extensions for detailed CUP characterization information
* extension contains 
    conducted 1..1 MS and
    matchedReference 0..1 MS
* extension[conducted].value[x] only boolean
* extension[conducted] ^short = "Molecular comparison conducted"
* extension[matchedReference].value[x] only Reference(OnconovaPrimaryCancerCondition or OnconovaSecondaryCancerCondition)
* extension[matchedReference] ^short = "Condition matched during molecular comparison"

Extension: MolecularTumorBoardCUPCharacterization
Id: onconova-ext-molecular-tumor-board-cup-characterization
Title: "Molecular Tumor Board CUP Characterization"
Description: "A characterization of the tumor board review focused on cancer of unknown primary (CUP) origin."

// Extensions for detailed CUP characterization information
* extension contains 
    conducted 1..1 MS and
    success 0..1 MS
* extension[conducted].value[x] only boolean
* extension[conducted] ^short = "CUP characterization conducted"
* extension[success].value[x] only boolean
* extension[success] ^short = "CUP characterization successful"