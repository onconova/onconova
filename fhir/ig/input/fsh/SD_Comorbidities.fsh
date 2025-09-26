Profile: OnconovaComorbidities
Parent: Comorbidities
Id: onconova-comorbidities
Title: "Comorbidities Profile"
Description: """
A profile representing comorbidities for a cancer patient, i.e. other health conditions that exist alongside the primary cancer diagnosis. Supports existing comorbidity panels such as the Charlson Comorbidity Index (CCI) and Elixhauser Comorbidity Index (ECI) with comorbidity indexes.

The profile constrains the mCODE [Comorbidities profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-comorbidities) to ensure consistent use of ICD-10 codes for documenting comorbid conditions, and to link the comorbidity information to the Onconova primary cancer condition profile. 
"""
* status = #final
* subject only Reference(OnconovaCancerPatient)
* focus only Reference(OnconovaPrimaryCancerCondition)

// Bind comorbidity panels to ComorbidityPanels value set
* method from ComorbidityPanels (required)

// Bind conditions to ICD-10 codes
* extension[comorbidConditionPresent].valueCodeableConcept from ICD10Conditions (required)
* extension[comorbidConditionAbsent].valueCodeableConcept from ICD10Conditions (required)

// Annotate unused elements for this profile
* insert NotUsed(encounter) 
* insert NotUsed(basedOn) 
* insert NotUsed(partOf) 
* insert NotUsed(issued) 
* insert NotUsed(interpretation) 
* insert NotUsed(derivedFrom) 
* insert NotUsed(referenceRange) 