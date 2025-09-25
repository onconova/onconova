Profile: OnconovaCancerFamilyMemberHistory
Parent: FamilyMemberHistory
Id: onconova-cancer-family-member-history
Title: "Cancer Family Member History"
Description: "A record of a family member's history of cancer."

// Basic constraints
* status = #completed
* deceased[x] only boolean

// Slice the condition element to include cancer conditions
* condition 1..* MS
* condition ^slicing.discriminator.type = #value
* condition ^slicing.discriminator.path = "code"
* condition ^slicing.rules = #open

// Profile the cancer condition slice
* condition contains cancerCondition 1..* MS
* condition[cancerCondition].code = http://snomed.info/sct#363346000 "Malignant neoplastic disease (disorder)" 
* condition[cancerCondition].onset[x] only Age
* condition[cancerCondition].extension contains CancerMorphology named morphology 0..1 MS
* condition[cancerCondition].extension contains CancerTopography named topography 0..1 MS

// Annotate unused inherited elements
* insert NotUsed(name)
* insert NotUsed(sex)
* insert NotUsed(born[x])
* insert NotUsed(age[x])
* insert NotUsed(estimatedAge)
* insert NotUsed(reasonCode)
* insert NotUsed(reasonReference)
