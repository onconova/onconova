Extension: CancerMorphology
Id: onconova-ext-cancer-morphology
Title: "Cancer Morphology"
Description: "The morphology of the cancer, represented by a ICD-O-3 code."
Context: Condition, OnconovaCancerFamilyMemberHistory.condition
* value[x] only CodeableConcept
* valueCodeableConcept from ICDO3MorphologyBehavior (required)

Extension: CancerTopography
Id: onconova-ext-cancer-topography
Title: "Cancer Topography"
Description: "The topography of the cancer, represented by a ICD-O-3 code."
Context: Condition, OnconovaCancerFamilyMemberHistory.condition
* value[x] only CodeableConcept
* valueCodeableConcept from ICDO3Topography (required)


