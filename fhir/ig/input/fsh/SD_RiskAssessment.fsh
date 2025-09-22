Profile: OnconovaCancerRiskAssessment
Id: mcode-cancer-risk-assessment
Parent: CancerRiskAssessment
Title: "Cancer Risk Assessment Profile"
Description: "This profile represents a risk assessment for cancer, including the type of cancer risk and the probability of developing that cancer."
* status = #final
* subject only Reference(OnconovaCancerPatient)
* code from CancerRiskAssessmentMethods (required)
* valueCodeableConcept from CancerRiskAssessmentValues (required)
* extension contains RiskAssessmentScore named riskAssessmentScore 0..1 // Numerical score of the risk assessment

Extension: RiskAssessmentScore
Id: onconova-ext-risk-assessment-score
Title: "Risk Assessment Score"
Description: "The numerical score of the risk assessment."
* value[x] only decimal or integer