Profile: OnconovaCancerRiskAssessment
Id: mcode-cancer-risk-assessment
Parent: CancerRiskAssessment
Title: "Onconova Cancer Risk Assessment Profile"
Description: """
Representation of a risk assessment performed for a cancer patient, including the method used, the resulting risk level, and an optional numerical score.

Conforms to the mCODE [CancerRiskAssessment](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-cancer-risk-assessment) profile and expands the valuesets for cancer risk assessment methods and values.
It also assumes for the status element the value 'final', as risk assessments within Onconova are collected based on finalized clinical records.
"""
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