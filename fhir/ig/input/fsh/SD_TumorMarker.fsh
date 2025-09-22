Profile: OnconovaTumorMarker
Id: onconova-tumor-marker
Title: "Onconova Tumor Marker Profile"
Parent: TumorMarkerTest
Description: "A profile representing a tumor marker observation for a cancer patient, including the type of tumor marker and its value. This profile extends the base mCODE TumorMarker profile to include specific constraints and requirements for Onconova."
* subject only Reference(OnconovaCancerPatient)
* extension contains TumorMarkerAnalyte named tumorMarkerAnalyte 1..1 // Specific analyte being measured

Extension: TumorMarkerAnalyte 
Id: onconova-ext-tumor-marker-analyte
Title: "Tumor Marker Analyte"
Description: "The specific analyte or substance being measured as a tumor marker, such as PSA, CA-125, or CEA."
* value[x] only CodeableConcept
* valueCodeableConcept from TumorMarkerAnalytes (required)