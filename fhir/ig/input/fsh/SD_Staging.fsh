Profile: OnconovaCancerStage 
Parent: CancerStage
Id: onconova-cancer-stage
Title: "Onconova Cancer Stage"
Description: "A profile representing the cancer stage for a cancer patient. This profile extends the base mCODE CancerStage resource to include specific constraints and extensions relevant to Onconova."      
* status = #final
* subject only Reference(OnconovaCancerPatient)

Profile: OnconovaTNMStageGroup 
Parent: TNMStageGroup
Id: onconova-tnm-stage-group
Title: "Onconova TNM Stage Group"
Description: "A profile representing the TNM stage group for a cancer patient. This profile extends the base mCODE TNMStageGroup resource to include specific constraints and extensions relevant to Onconova."      
* status = #final
* subject only Reference(OnconovaCancerPatient)
* hasMember only Reference(
    OnconovaTNMPrimaryTumorCategory or 
    OnconovaTNMRegionalNodesCategory or 
    OnconovaTNMDistantMetastasesCategory or 
    OnconovaTNMLymphaticInvasionCategory or 
    OnconovaTNMPerineuralInvasionCategory or 
    OnconovaTNMResidualTumorCategory or 
    OnconovaSerumTumorMarkerLevelCategory or 
    OnconovaAneuploidScore or 
    OnconovaTNMGradeCategory
)

Profile: OnconovaTNMPrimaryTumorCategory 
Parent: TNMPrimaryTumorCategory
Id: onconova-tnm-primary-tumor-category
Title: "Onconova TNM Primary Tumor Category"
Description: "A profile representing the TNM primary tumor category for a cancer patient. This profile extends the base mCODE TNMPrimaryTumorCategory resource to include specific constraints and extensions relevant to Onconova."      
* status = #final
* subject only Reference(OnconovaCancerPatient)
* valueCodeableConcept from TNMPrimaryTumorCategories (required)


Profile: OnconovaTNMDistantMetastasesCategory 
Parent: TNMDistantMetastasesCategory
Id: onconova-tnm-distant-metastases-category
Title: "Onconova TNM Distant Metastases Category"
Description: "A profile representing the TNM distant metastases category for a cancer patient. This profile extends the base mCODE TNMDistantMetastasesCategory resource to include specific constraints and extensions relevant to Onconova."      
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* valueCodeableConcept from TNMDistantMetastasisCategories (required)


Profile: OnconovaTNMRegionalNodesCategory 
Parent: TNMRegionalNodesCategory
Id: onconova-tnm-regional-nodes-category
Title: "Onconova TNM Regional Nodes Category"
Description: "A profile representing the TNM regional nodes category for a cancer patient. This profile extends the base mCODE TNMRegionalNodesCategory resource to include specific constraints and extensions relevant to Onconova."      
* status = #final
* subject only Reference(OnconovaCancerPatient)
* valueCodeableConcept from TNMRegionalNodesCategories (required)

Profile: OnconovaTNMLymphaticInvasionCategory 
Parent: TNMCategory
Id: onconova-tnm-lymphatic-invasion-category
Title: "Onconova TNM Lymphatic Invasion Category"
Description: "A profile representing the TNM lymphatic invasion category for a cancer patient. This profile extends the base mCODE TNMCategory resource to include specific constraints and extensions relevant to Onconova."      
* status = #final
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#385414009 "Lymphatic (small vessel) tumor invasion finding (finding)"
* valueCodeableConcept from TNMLymphaticInvasionCategories (required)

Profile: OnconovaTNMPerineuralInvasionCategory 
Parent: TNMCategory
Id: onconova-tnm-perineural-invasion-category
Title: "Onconova TNM Perineural Invasion Category"
Description: "A profile representing the TNM perineural invasion category for a cancer patient. This profile extends the base mCODE TNMCategory resource to include specific constraints and extensions relevant to Onconova."      
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#396394004 "Perineural invasion finding (finding)"
* valueCodeableConcept from TNMPerineuralInvasionCategories (required)

Profile: OnconovaTNMResidualTumorCategory 
Parent: TNMCategory
Id: onconova-tnm-residual-tumor-category
Title: "Onconova TNM Residual Tumor Category"
Description: "A profile representing the TNM residual tumor category for a cancer patient. This profile extends the base mCODE TNMCategory resource to include specific constraints and extensions relevant to Onconova."      
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#37161004 "Finding of residual tumor (finding)"
* valueCodeableConcept from TNMResidualTumorCategories (required)

Profile: OnconovaSerumTumorMarkerLevelCategory
Parent: TNMCategory 
Id: onconova-serous-tumor-marker-level-category
Title: "Onconova Serum Tumor Marker Level Category"
Description: "A profile representing the serum tumor marker level category for a cancer patient. This profile extends the base mCODE TNMCategory resource to include specific constraints and extensions relevant to Onconova."      
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#396701002  "Finding of serum tumor marker level (finding)"
* valueCodeableConcept from TNMSerumTumorMarkerLevelCategories (required)

Profile: OnconovaVenousInvasionCategory
Parent: TNMCategory 
Id: onconova-venous-invasion-category
Title: "Onconova Venous Invasion Category"
Description: "A profile representing the venous invasion category for a cancer patient. This profile extends the base mCODE TNMCategory resource to include specific constraints and extensions relevant to Onconova."    
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* code = $SNOMED#369732007 "Venous (large vessel) tumor invasion finding (finding)"
* valueCodeableConcept from TNMVenousInvasionCategories (required)

Profile: OnconovaTNMGradeCategory 
Parent: TNMCategory
Id: onconova-tnm-grade-category
Title: "Onconova TNM Grade Category"
Description: "A profile representing the TNM grade category for a cancer patient. This profile extends the base mCODE TNMCategory resource to include specific constraints and extensions relevant to Onconova."      
* status = #final   
* subject only Reference(OnconovaCancerPatient)
* code from TNMGradeCategoryMethods (required)
* valueCodeableConcept from TNMGradeCategories (required)   
