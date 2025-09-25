Profile: OnconovaECOGPerformanceStatus
Parent: ECOGPerformanceStatus
Id: onconova-ecog-performance-status
Title: "ECOG Performance Status Profile"
Description: "A profile representing ECOG Performance Status for a cancer patient." 

* status = #final
* subject only Reference(OnconovaCancerPatient)
* focus only Reference(OnconovaPrimaryCancerCondition)

Profile: OnconovaKarnofskyPerformanceStatus
Parent: KarnofskyPerformanceStatus
Id: onconova-Karnofsky-performance-status
Title: "Karnofsky Performance Status Profile"
Description: "A profile representing Karnofsky Performance Status for a cancer patient." 

* status = #final
* subject only Reference(OnconovaCancerPatient)
* focus only Reference(OnconovaPrimaryCancerCondition)