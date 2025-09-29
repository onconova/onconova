Profile: OnconovaCancerFamilyMemberHistory
Parent: FamilyMemberHistory
Id: onconova-cancer-family-member-history
Title: "Cancer Family Member History"
Description: """
A profile recording of a family member's history of cancer.

This profile is based on the core FHIR `FamilyMemberHistory` resource rather than the mCODE  [HistoryOfMetastaticCancer profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-history-of-metastatic-cancer) to allow for a broader range of cancer history documentation (not limited to metastatic cancer). It includes constraints to ensure that at least one cancer condition is recorded, along with optional extensions for cancer morphology and topography.
"""

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
