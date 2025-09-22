Profile: OnconovaGenomicVariant
Parent: GenomicVariant
Id: onconova-genomic-variant
Title: "Onconova Genomic Variant Profile"
Description: "A profile representing genomic variants for a cancer patient. This profile extends the base mCODE GenomicVariant resource to include specific constraints and extensions relevant to Onconova."

* status = #final
* subject only Reference(OnconovaCancerPatient)

* insert CreateComponent(nucleotidesCount, 1, 1)
* component[nucleotidesCount].code = $NCIT#C709 "Nucleotides"
* component[nucleotidesCount].value[x] only integer

* insert CreateComponent(geneFeature, 1, 1)
* component[geneFeature].code = $NCIT#C13445  "Gene Feature"
* component[geneFeature].value[x] only string

