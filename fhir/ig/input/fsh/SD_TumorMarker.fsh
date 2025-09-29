Profile: OnconovaTumorMarker
Id: onconova-tumor-marker
Title: "Tumor Marker Profile"
Parent: TumorMarkerTest
Description: """
A profile representing a tumor marker observation for a cancer patient, including the type of tumor marker and its value. 

This profile extends the base mCODE [TumorMarkerTest profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-tumor-marker-test) to include specific constraints and requirements for Onconova.

If relied on the same use context as mCODE, namely for substances found in tissue or blood or other body fluids that may be a sign of cancer or certain benign (non-cancer) conditions measured at the levels of the protein and substance post-RNA protein synthesis (not at genomic level).
"""
* subject only Reference(OnconovaCancerPatient)
* extension contains TumorMarkerAnalyte named tumorMarkerAnalyte 1..1 // Specific analyte being measured

//==================
// Extensions
//==================

Extension: TumorMarkerAnalyte 
Id: onconova-ext-tumor-marker-analyte
Title: "Tumor Marker Analyte"
Description: "The specific analyte or substance being measured as a tumor marker, such as PSA, CA-125, or CEA."
* value[x] only CodeableConcept
* valueCodeableConcept from TumorMarkerAnalytes (required)