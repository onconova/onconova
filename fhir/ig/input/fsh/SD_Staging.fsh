Profile: OnconovaCancerStage 
Parent: CancerStage
Id: onconova-cancer-stage
Title: "Cancer Stage"
Description: """
A profile representing the cancer stage for a cancer patient. 

It constrains the mCODE [CancerStage profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-cancer-stage) to include specific constraints and extensions relevant to Onconova.
"""      
* status = #final
* subject only Reference(OnconovaCancerPatient)

Profile: OnconovaTNMStageGroup 
Parent: TNMStageGroup
Id: onconova-tnm-stage-group
Title: "TNM Stage Group"
Description: """
A profile representing the TNM stage group for a cancer patient. 

It extends the base mCODE [TNMStageGroup profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tnm-stage-group) to expand the TNM subcategories and include specific constraints and extensions relevant to Onconova.
"""      
* status = #final
* subject only Reference(OnconovaCancerPatient)
* hasMember only Reference(
    TNMCategory
)

// Set profiles for existing slice
* hasMember[TNMCategory] only Reference(
    OnconovaTNMPrimaryTumorCategory or 
    OnconovaTNMDistantMetastasesCategory or 
    OnconovaTNMRegionalNodesCategory
)
// Add additional slices for the other TNM category profiles
* hasMember contains lymphaticInvasionCategory 0..1 
* hasMember[lymphaticInvasionCategory] only Reference(OnconovaTNMLymphaticInvasionCategory)
* hasMember contains perineuralInvasionCategory 0..1 
* hasMember[perineuralInvasionCategory] only Reference(OnconovaTNMPerineuralInvasionCategory)
* hasMember contains residualTumorCategory 0..1 
* hasMember[residualTumorCategory] only Reference(OnconovaTNMResidualTumorCategory)
* hasMember contains serumTumorMarkerLevelCategory 0..1 
* hasMember[serumTumorMarkerLevelCategory] only Reference(OnconovaTNMSerumTumorMarkerLevelCategory)
* hasMember contains gradeCategory 0..1 
* hasMember[gradeCategory] only Reference(OnconovaTNMGradeCategory)
* hasMember contains venousInvasionCategory 0..1 
* hasMember[venousInvasionCategory] only Reference(OnconovaTNMVenousInvasionCategory)


Profile: OnconovaTNMPrimaryTumorCategory 
Parent: TNMPrimaryTumorCategory
Id: onconova-tnm-primary-tumor-category
Title: "TNM Primary Tumor Category"
Description: """
A profile representing the TNM primary tumor category for a cancer patient. 

This profile extends the base mCODE [TNMPrimaryTumorCategory profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tnm-primary-tumor-category) to include specific constraints and extensions relevant to Onconova.
"""      
* status = #final
* subject only Reference(OnconovaCancerPatient)
* valueCodeableConcept from TNMPrimaryTumorCategories (required)


Profile: OnconovaTNMDistantMetastasesCategory 
Parent: TNMDistantMetastasesCategory
Id: onconova-tnm-distant-metastases-category
Title: "TNM Distant Metastases Category"
Description: """
A profile representing the TNM distant metastases category for a cancer patient. 

This profile extends the base mCODE [TNMDistantMetastasesCategory profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tnm-distant-metastases-category) to include specific constraints and extensions relevant to Onconova.
"""
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* valueCodeableConcept from TNMDistantMetastasisCategories (required)


Profile: OnconovaTNMRegionalNodesCategory 
Parent: TNMRegionalNodesCategory
Id: onconova-tnm-regional-nodes-category
Title: "TNM Regional Nodes Category"
Description: """
A profile representing the TNM regional nodes category for a cancer patient. 

This profile extends the base mCODE [TNMRegionalNodesCategory profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tnm-regional-nodes-category) to include specific constraints and extensions relevant to Onconova.
"""
* status = #final
* subject only Reference(OnconovaCancerPatient)
* valueCodeableConcept from TNMRegionalNodesCategories (required)

Profile: OnconovaTNMLymphaticInvasionCategory 
Parent: TNMCategory
Id: onconova-tnm-lymphatic-invasion-category
Title: "TNM Lymphatic Invasion Category"
Description: """
A profile representing the TNM lymphatic invasion category for a cancer patient. 

This profile extends the base mCODE [TNMCategory profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tnm-category) to specify the new TNM category.
"""
* status = #final
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#385414009 "Lymphatic (small vessel) tumor invasion finding (finding)"
* valueCodeableConcept from TNMLymphaticInvasionCategories (required)

Profile: OnconovaTNMPerineuralInvasionCategory 
Parent: TNMCategory
Id: onconova-tnm-perineural-invasion-category
Title: "TNM Perineural Invasion Category"
Description: """
A profile representing the TNM perineural invasion category for a cancer patient. 

This profile extends the base mCODE [TNMCategory profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tnm-category) to specify the new TNM category.
"""
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#396394004 "Perineural invasion finding (finding)"
* valueCodeableConcept from TNMPerineuralInvasionCategories (required)

Profile: OnconovaTNMResidualTumorCategory 
Parent: TNMCategory
Id: onconova-tnm-residual-tumor-category
Title: "TNM Residual Tumor Category"
Description: """
A profile representing the TNM residual tumor category for a cancer patient.

This profile extends the base mCODE [TNMCategory profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tnm-category) to specify the new TNM category.
"""
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#37161004 "Finding of residual tumor (finding)"
* valueCodeableConcept from TNMResidualTumorCategories (required)

Profile: OnconovaTNMSerumTumorMarkerLevelCategory
Parent: TNMCategory 
Id: onconova-serous-tumor-marker-level-category
Title: "Serum Tumor Marker Level Category"
Description: """
A profile representing the serum tumor marker level category for a cancer patient. 

This profile extends the base mCODE [TNMCategory profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tnm-category) to specify the new TNM category.
"""
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#396701002  "Finding of serum tumor marker level (finding)"
* valueCodeableConcept from TNMSerumTumorMarkerLevelCategories (required)

Profile: OnconovaTNMVenousInvasionCategory
Parent: TNMCategory 
Id: onconova-venous-invasion-category
Title: "Venous Invasion Category"
Description: """
A profile representing the venous invasion category for a cancer patient. 

This profile extends the base mCODE [TNMCategory profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tnm-category) to specify the new TNM category.
"""   
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#369732007 "Venous (large vessel) tumor invasion finding (finding)"
* valueCodeableConcept from TNMVenousInvasionCategories (required)

Profile: OnconovaTNMGradeCategory 
Parent: TNMCategory
Id: onconova-tnm-grade-category
Title: "TNM Grade Category"
Description: """
A profile representing the TNM grade category for a cancer patient. 

This profile extends the base mCODE [TNMCategory profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tnm-category) to specify the new TNM category.
"""
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* code from TNMGradeCategoryMethods (required)
* valueCodeableConcept from TNMGradeCategories (required)   
