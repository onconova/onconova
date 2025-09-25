Profile: OnconovaPrimaryCancerCondition
Id: onconova-primary-cancer-condition
Title: "Primary Cancer Condition Profile"
Parent: PrimaryCancerCondition
Description: "Records the primary cancer condition, the original or first neoplasm in the body (Definition from: [NCI Dictionary of Cancer Terms](https://www.cancer.gov/publications/dictionaries/cancer-terms/def/primary-tumor)). Cancers that are not clearly secondary (i.e., of uncertain origin or behavior) should be documented as primary."
* subject only Reference(OnconovaCancerPatient)
* extension contains RecurrenceOf named recurrenceOf 0..1 // Indicates that the condition is a recurrence of a previous condition

Profile: OnconovaSecondaryCancerCondition
Parent: SecondaryCancerCondition
Id: onconova-secondary-cancer-condition
Title: "Secondary Cancer Condition Profile"
Description: "Records the history of secondary neoplasms, including location(s) and the date of onset of metastases. A secondary cancer results from the spread (metastasization) of cancer from its original site (Definition from: NCI Dictionary of Cancer Terms)."
* subject only Reference(OnconovaCancerPatient)

Extension: RecurrenceOf
Id: onconova-ext-recurrence-of
Title: "Recurrence Of"
Description: "Indicates that the condition is a recurrence of a previous condition, and provides a reference to that previous condition."
* value[x] only Reference(PrimaryCancerCondition)