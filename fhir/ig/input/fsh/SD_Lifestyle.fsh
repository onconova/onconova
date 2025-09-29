Profile: OnconovaLifestyle
Parent: USCoreSimpleObservationProfile
Id: onconova-lifestyle
Title: "Lifestyle Profile"
Description: """
A profile representing a (reported) observation on certain lifestyle characteristics of a cancer patient (e.g. smoking, drinking, and sleeping habits, environmental exposures, etc.). 

It directly profiles the base FHIR `Observation` resource as this resource is not represented in mCODE, to add relevant observation components for the different lifestyle characteristics. 
"""

* subject only Reference(OnconovaCancerPatient)
* status = #final
* code = $LOINC#LA32823-9 "Lifestyle"

// Initiate slicing of components
* insert ObservationComponentSlicingRules

// Add smoking status component
* insert CreateComponent(smokingStatus, 0, 1)
* component[smokingStatus].code = $LOINC#72166-2 "Tobacco smoking status"
* component[smokingStatus].value[x] only CodeableConcept
* component[smokingStatus].valueCodeableConcept from SmokingStatus

// Add smoking pack-years component
* insert CreateComponent(smokingPackyears, 0, 1)
* component[smokingPackyears].code = $LOINC#8664-5 "Cigarettes smoked total (pack per year) - Reported"
* component[smokingPackyears].value[x] only Quantity
* component[smokingPackyears].valueQuantity.system = $UCUM
* component[smokingPackyears].valueQuantity.code = $UCUM#{pack-year}

// Add smoking quited component
* insert CreateComponent(smokingQuited, 0, 1)
* component[smokingQuited].code = $LOINC#107339-4 "Temporary smoking cessation [Time]"
* component[smokingQuited].value[x] only Quantity
* component[smokingQuited].valueQuantity from UnitsOfTime

// Add alcohol consumption component
* insert CreateComponent(alcoholConsumption, 0, 1)
* component[alcoholConsumption].code = $LOINC#1106630-7 "Alcohol use pattern"
* component[alcoholConsumption].value[x] only CodeableConcept
* component[alcoholConsumption].valueCodeableConcept from http://loinc.org/vs/LL2179-1

// Add night sleep component
* insert CreateComponent(nightSleep, 0, 1)
* component[nightSleep].code = $LOINC#93832-4 "Sleep duration"
* component[nightSleep].value[x] only Quantity
* component[nightSleep].valueQuantity from UnitsOfTime

// Add recreational drug component
* insert CreateComponent(recreationalDrug, 0, *)
* component[recreationalDrug].code = $NCIT#C84368 "Recreational Drug"
* component[recreationalDrug].value[x] only CodeableConcept
* component[recreationalDrug].valueCodeableConcept from RecreationalDrugs

// Add exposures component
* insert CreateComponent(exposures, 0, *)
* component[exposures].code = $NCIT#C16552 "Environmental Exposure"
* component[exposures].value[x] only CodeableConcept
* component[exposures].valueCodeableConcept from ExposureAgents 

// Annotate unused elements for this profile
* insert NotUsed(focus)
* insert NotUsed(encounter)
* insert NotUsed(issued)
* insert NotUsed(performer)
* insert NotUsed(bodySite)
* insert NotUsed(interpretation)
* insert NotUsed(specimen)
* insert NotUsed(device)    
* insert NotUsed(referenceRange)
* insert NotUsed(hasMember)