ValueSet: TNMPrimaryTumorCategories
Id: onconova-vs-tnm-primary-tumor-categories
Title: "TNM Primary Tumor Categories"
Description: "TNM Primary Tumor Categories Value Set"

* include codes from valueset http://hl7.org/fhir/us/mcode/ValueSet/mcode-tnm-primary-tumor-category-vs

* include codes from system $SNOMED where concept descendent-of #1279738002
* include codes from system $SNOMED where concept descendent-of #1279573003


ValueSet: TNMRegionalNodesCategories
Id: onconova-vs-tnm-regional-nodes-categories
Title: "TNM Regional Nodes Categories Value Set"
Description: "TNM Regional Nodes Categories Value Set"

* include codes from valueset http://hl7.org/fhir/us/mcode/ValueSet/mcode-tnm-regional-nodes-category-vs

* include codes from system $SNOMED where concept descendent-of #1279799007
* include codes from system $SNOMED where concept descendent-of #1279850004


ValueSet: TNMDistantMetastasisCategories
Id: onconova-vs-tnm-distant-metastasis-categories
Title: "TNM Distant Metastasis Categories Value Set"
Description: "TNM Distant Metastasis Categories Value Set"

* include codes from valueset http://hl7.org/fhir/us/mcode/ValueSet/mcode-tnm-distant-metastases-category-vs

* include codes from system $SNOMED where concept descendent-of #1281794006
* include codes from system $SNOMED where concept descendent-of #1281795007


ValueSet: TNMLymphaticInvasionCategories
Id: onconova-tnm-lymphatic-invasion-categories
Title: "TNM Lymphatic Invasion Categories Value Set"
Description: "TNM Lymphatic Invasion Categories Value Set"

* $SNOMED#44649003 "L0 stage"
* $SNOMED#74139005 "L1 stage"
* $SNOMED#72632003 "L2 stage"
* $SNOMED#33419001 "LX stage"


ValueSet: TNMPerineuralInvasionCategories
Id: onconova-tnm-perineural-invasion-categories
Title: "TNM Perineural Invasion Categories Value Set"
Description: "TNM Perineural Invasion Categories Value Set"

* $SNOMED#370051000 "Stage Pn0"
* $SNOMED#369731000 "Stage Pn1"


ValueSet: TNMResidualTumorCategories
Id: onconova-tnm-residual-tumor-categories
Title: "TNM Residual Tumor Categories Value Set"
Description: "TNM Residual Tumor Categories Value Set"

* include codes from system $SNOMED where concept descendent-of #1222601005

ValueSet: TNMSerumTumorMarkerLevelCategories
Id: onconova-vs-tnm-serum-tumor-marker-level-categories
Title: "TNM Serum Tumor Marker Level Categories Value Set"
Description: "TNM Serum Tumor Marker Level Categories Value Set"

* $SNOMED#313139000 "Stage S0"
* $SNOMED#313140003 "Stage S1"
* $SNOMED#313141004 "Stage S2"
* $SNOMED#313142006 "Stage S3"
* $SNOMED#313138008 "Stage SX"


ValueSet: TNMVenousInvasionCategories
Id: onconova-vs-tnm-venous-invasion-categories
Title: "TNM Venous Invasion Categories Value Set"
Description: "TNM Venous Invasion Categories Value Set"

* $SNOMED#6510002 "VX stage"
* $SNOMED#40223008 "V0 stage"
* $SNOMED#67302005 "V1 stage"
* $SNOMED#50064003 "V2 stage"


ValueSet: TNMGradeCategoryMethods
Id: onconova-vs-tnm-grade-category-methods
Title: "TNM Grade Category Methods Value Set"
Description: "TNM Grade Category Methods Value Set"

* $SNOMED#1222598000 
* $SNOMED#1222599008
* $SNOMED#1222600006

ValueSet: TNMGradeCategories
Id: onconova-vs-tnm-grade-categories
Title: "TNM Grade Categories Value Set"
Description: "TNM Grade Categories Value Set"

* $SNOMED#1228848004
* $SNOMED#1228850007
* $SNOMED#1228851006
* $SNOMED#1228852004
* $SNOMED#1259951003
* $SNOMED#1228847009
* $SNOMED#1228845001
* $SNOMED#1228854003
* $SNOMED#1228853009