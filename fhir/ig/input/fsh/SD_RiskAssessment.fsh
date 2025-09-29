Profile: OnconovaCancerRiskAssessment
Parent: CancerRiskAssessment
Id: onconova-cancer-risk-assessment
Title: "Cancer Risk Assessment Profile"
Description: """
A profile representing a risk assessment performed for a cancer patient, including the method used, the resulting risk level, and an optional numerical score.

It constraints the mCODE [CancerRiskAssessment profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-cancer-risk-assessment) and expands the valuesets for cancer risk assessment methods and values.
"""
* status = #final
* subject only Reference(OnconovaCancerPatient)
* code from CancerRiskAssessmentMethods (required)
* valueCodeableConcept from CancerRiskAssessmentValues (required)

// Add extension for numerical score of the risk assessment
* extension contains RiskAssessmentScore named riskAssessmentScore 0..1 

//======================
// Extensions
//======================

Extension: RiskAssessmentScore
Id: onconova-ext-risk-assessment-score
Title: "Risk Assessment Score"
Description: "The numerical score of the risk assessment."
* value[x] only decimal or integer