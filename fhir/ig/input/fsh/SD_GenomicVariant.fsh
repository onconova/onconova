Profile: OnconovaGenomicVariant
Parent: GenomicVariant
Id: onconova-genomic-variant
Title: "Genomic Variant Profile"
Description: """
A profile representing a genomic variant identified for a cancer patient. 

This profile extends the base mCODE [GenomicVariant profile](http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-genomic-variant) (which in turn profiles the Genomics Reporting [Variant profile](http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/variant)) to include specific constraints and extensions relevant to Onconova.
"""

* status = #final
* subject only Reference(OnconovaCancerPatient)

* insert CreateComponent(nucleotidesCount, 1, 1) 
* component[nucleotidesCount].code = $NCIT#C709 "Nucleotides"
* component[nucleotidesCount].value[x] only integer

* insert CreateComponent(geneFeature, 1, 1)
* component[geneFeature].code = $NCIT#C13445  "Gene Feature"
* component[geneFeature].value[x] only string

