Profile: OnconovaImagingDiseaseStatus
Parent: CancerDiseaseStatus
Id: onconova-imaging-disease-status
Title: "Imaging Disease Status Profile"
Description: """
A profile representing the imaging-based disease status of a cancer patient.

It constrains the mCODE [CancerDiseaseStatus profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-cancer-disease-status) to restrict it to imaging-based monitoring evaluated based on RECIST criteria.
"""

* status = #final

// Use Onconova profile references
* subject only Reference(OnconovaCancerPatient)
* focus only Reference(OnconovaPrimaryCancerCondition or OnconovaSecondaryCancerCondition)

// Fix the the of evidence to imaging
* category = http://terminology.hl7.org/CodeSystem/observation-category#imaging "Imaging"
* extension[evidenceType].valueCodeableConcept = $SNOMED#363679005 "Imaging (procedure)"

// Constrain the valuesets
* method from CancerImagingMethods (required)
* bodySite from ObservationBodySites (required)

// Annotate unused elements
* insert NotUsed(specimen)
* insert NotUsed(performer)
* insert NotUsed(device)
* insert NotUsed(referenceRange)
* insert NotUsed(derivedFrom)
* insert NotUsed(basedOn)
* insert NotUsed(partOf)
* insert NotUsed(encounter)
* insert NotUsed(component)

//==================
// Extensions
//==================

Extension: RecistIsInterpreted
Id: onconova-ext-recist-is-interpreted
Title: "Recist Is Interpreted"
Description: "Indicates that whether the RECIST was interpreted from a radiology report rather than extracted."
* value[x] only boolean
