Profile: OnconovaImagingDiseaseStatus
Parent: CancerDiseaseStatus
Id: onconova-imaging-disease-status
Title: "Imaging Disease Status Profile"
Description: "A profile representing the imaging-based disease status of a cancer patient, including specific constraints and extensions relevant to Onconova."

* subject only Reference(OnconovaCancerPatient)

* extension[evidenceType].valueCodeableConcept = $SNOMED#363679005 "Imaging (procedure)"

* status = #final

* method from CancerImagingMethods (required)

* focus only Reference(OnconovaPrimaryCancerCondition or OnconovaSecondaryCancerCondition)

* bodySite from ObservationBodySites (required)

* insert NotUsed(specimen)
* insert NotUsed(performer)
* insert NotUsed(device)
* insert NotUsed(referenceRange)
* insert NotUsed(component)
