Profile: OnconovaTumorMutationalBurden  
Parent: TMB
Id: onconova-tumor-mutational-burden
Title: "Tumor Mutational Burden Profile"
Description: "A profile representing tumor mutational burden for a cancer patient. This profile extends the base GenomicsReporting TumorMutationalBurden resource to include specific constraints and extensions relevant to Onconova."

* status = #final
* subject only Reference(OnconovaCancerPatient)

Profile: OnconovaMicrosatelliteInstability
Parent: MSI
Id: onconova-microsatellite-instability
Title: "Microsatellite Instability Profile"
Description: "A profile representing microsatellite instability for a cancer patient. This profile extends the base GenomicsReporting MicrosatelliteInstability resource to include specific constraints and extensions relevant to Onconova."

* status = #final
* subject only Reference(OnconovaCancerPatient)


Profile: OnconovaLossOfHeterozygosity
Parent: GenomicsBase
Id: onconova-loss-of-heterozygosity
Title: "Loss of Heterozygosity Profile"
Description: "A profile representing loss of heterozygosity for a cancer patient. This profile extends the base GenomicsReporting GenomicsBase resource to include specific constraints and extensions relevant to Onconova."

* status = #final
* subject only Reference(OnconovaCancerPatient)
* code = $NCIT#C18016 "Loss of Heterozygosity"
* value[x] only Quantity
* valueQuantity 1..1
* valueQuantity.system = $UCUM
* valueQuantity.code = $UCUM#%
* insert NotUsed(interpretation)


Profile: OnconovaHomologousRecombinationDeficiency
Parent: GenomicsBase
Id: onconova-homologous-recombination-deficiency
Title: "Homologous Recombination Deficiency Profile"
Description: "A profile representing homologous recombination deficiency for a cancer patient. This profile extends the base GenomicsReporting GenomicsBase resource to include specific constraints and extensions relevant to Onconova."

* status = #final
* subject only Reference(OnconovaCancerPatient)
* code = $NCIT#C120465 "Homologous Recombination Deficiency"
* value[x] only Quantity
* valueQuantity 1..1
* valueQuantity.system = $UCUM
* valueQuantity.code = $UCUM#1
* interpretation from https://loinc.org/LL2038-9 (required)


Profile: OnconovaTumorNeoantigenBurden
Parent: GenomicsBase
Id: onconova-tumor-neoantigen-burden
Title: "Tumor Neoantigen Burden Profile"
Description: "A profile representing tumor neoantigen burden for a cancer patient. This profile extends the base GenomicsReporting GenomicsBase resource to include specific constraints and extensions relevant to Onconova."  

* status = #final
* subject only Reference(OnconovaCancerPatient)
* code = $TBD#tumor-neoantigen-burden "Tumor Neoantigen Burden"
* value[x] only Quantity 
* valueQuantity 1..1 
* valueQuantity.system = $UCUM
* valueQuantity.code = $UCUM#1/1000000{Neoantigen}
* insert NotUsed(interpretation)


Profile: OnconovaAneuploidScore
Parent: GenomicsBase
Id: onconova-aneuploid-score
Title: "Aneuploid Score Profile"
Description: "A profile representing aneuploid score for a cancer patient. This profile extends the base GenomicsReporting GenomicsBase resource to include specific constraints and extensions relevant to Onconova."

* status = #final
* subject only Reference(OnconovaCancerPatient)
* code = $TBD#aneuploid-score "Aneuploid Score"
* value[x] only Quantity
* valueQuantity 1..1
* valueQuantity.system = $UCUM
* valueQuantity.code = $UCUM#1
* insert NotUsed(interpretation)