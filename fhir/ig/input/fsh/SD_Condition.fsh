Profile: OnconovaPrimaryCancerCondition
Id: onconova-primary-cancer-condition
Title: "Onconova Primary Cancer Condition Profile"
Parent: PrimaryCancerCondition
Description: "Records the primary cancer condition, the original or first neoplasm in the body (Definition from: [NCI Dictionary of Cancer Terms](https://www.cancer.gov/publications/dictionaries/cancer-terms/def/primary-tumor)). Cancers that are not clearly secondary (i.e., of uncertain origin or behavior) should be documented as primary."
* subject only Reference(OnconovaCancerPatient)

Profile: OnconovaSecondaryCancerCondition
Parent: SecondaryCancerCondition
Id: onconova-secondary-cancer-condition
Title: "Onconova Secondary Cancer Condition Profile"
Description: "Records the history of secondary neoplasms, including location(s) and the date of onset of metastases. A secondary cancer results from the spread (metastasization) of cancer from its original site (Definition from: NCI Dictionary of Cancer Terms)."
* subject only Reference(OnconovaCancerPatient)