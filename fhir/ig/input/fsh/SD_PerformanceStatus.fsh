Profile: OnconovaECOGPerformanceStatus
Parent: ECOGPerformanceStatus
Id: onconova-ecog-performance-status
Title: "ECOG Performance Status Profile"
Description: """
A profile representing ECOG performance status score for a cancer patient.

Adds minimal constraints to the mCODE [`ECOGPerformanceStatus` profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-ecog-performance-status) to account for Onconova specifics.
""" 

* status = #final
* subject only Reference(OnconovaCancerPatient)
* focus only Reference(OnconovaPrimaryCancerCondition)

// Annotate unused elements
* insert NotUsed(derivedFrom)
* insert NotUsed(referenceRange)
* insert NotUsed(method)
* insert NotUsed(dataAbsentReason)
* insert NotUsed(performer)
* insert NotUsed(encounter)
* insert NotUsed(focus)
* insert NotUsed(issued)
* insert NotUsed(partOf)
* insert NotUsed(basedOn)

Profile: OnconovaKarnofskyPerformanceStatus
Parent: KarnofskyPerformanceStatus
Id: onconova-Karnofsky-performance-status
Title: "Karnofsky Performance Status Profile"
Description: """
A profile representing the Karnofsky performance status score for a cancer patient.

Adds minimal constraints to the mCODE [KarnofskyPerformanceStatus profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-karnofsky-performance-status) to account for Onconova specifics.
""" 

* status = #final
* subject only Reference(OnconovaCancerPatient)
* focus only Reference(OnconovaPrimaryCancerCondition)

// Annotate unused elements
* insert NotUsed(derivedFrom)
* insert NotUsed(referenceRange)
* insert NotUsed(method)
* insert NotUsed(dataAbsentReason)
* insert NotUsed(performer)
* insert NotUsed(encounter)
* insert NotUsed(focus)
* insert NotUsed(issued)
* insert NotUsed(partOf)
* insert NotUsed(basedOn)