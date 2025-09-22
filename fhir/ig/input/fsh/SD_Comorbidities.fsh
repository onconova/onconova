Profile: OnconovaComorbidities
Parent: Comorbidities
Id: onconova-comorbidities
Title: "Onconova Comorbidities Profile"
Description: "A profile representing comorbidities for a cancer patient."

* status = #final

// Reference Onconova resources
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