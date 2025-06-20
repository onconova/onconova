# Data Protection and Security in POP

## Why Data Protection Matters

The **Precision Oncology Platform (POP)** handles sensitive clinical and research data, which may include **Protected Health Information (PHI)**.  Ensuring the privacy and security of this data is both an ethical obligation and a legal requirement under various regulations, such as:

- **GDPR (General Data Protection Regulation)** in the European Union
- **HIPAA (Health Insurance Portability and Accountability Act)** in the United States
- Local and institutional data protection policies and ethics board guidelines

Failing to properly manage sensitive data can result in:

- Legal penalties and regulatory sanctions
- Data breaches and loss of patient trust
- Irreparable harm to research integrity

!!! note

    **Each site is accountable for maintaining a compliant environment**. No software is inherently compliant; compliance depends on the environment in which it’s implemented. This includes the policies, procedures, and infrastructure managed by each study team and institution. Decisions about server settings, security, data backups, and user access are the responsibility of each organization — not defined by POP itself. 

---

## Pseudonymized vs. Anonymized Data

Understanding the difference between **pseudonymized** and **anonymized** data is crucial in data protection workflows:

| Concept         | Description                                                                 | Re-identification Possible |
|:----------------|:----------------------------------------------------------------------------|:---------------------------|
| **Pseudonymized Data** | Direct identifiers (names, IDs) are replaced with a code, but a separate key exists that can link data back to the individual. | **Yes** |
| **Anonymized Data**    | All identifying information is removed or irreversibly transformed, making it impossible to link data back to a person. | **No** |

**POP supports both modes of data handling, depending on the operational context and user permissions.**

At the **database-level**, all data are considered **pseudonymized** with the clinical identifier being the primary re-identification mechanism if the source EHR system is accessible. 
At the **API-level** (and by extension to all end-users), the data is by default presented **anmonymized**. Users with elevated rights can access the pseudonymized under certain conditions. 

---

## Anonymization Methods in POP

To protect sensitive healthcare information during data management and analysis, POP implements anonymization strategies aligned with the **HIPAA Safe Harbor De-identification Standard**, which outlines specific identifiers that must be removed or altered to consider data de-identified. The following table describes each HIPAA criterion and how POP handles it:

| **HIPAA Identifier** | **Description** | **Collected in POP** | **POP Anonymization Implementation** |
|:---------------------|:----------------|:----------------------|:--------------------------------------|
| **Names** | Full names, initials | No | |
| **Geographic subdivisions smaller than a state** | Street address, city, ZIP codes (except first 3 digits if population > 20,000) | No | |
| **All elements of dates (except year) directly related to an individual** | Birth date, admission date, discharge date, death date, etc. | Month and year of birth and death | Not exposed to end-users
| **All other dates** | Lab result date, therapy period, etc. | Yes | Random Date Shifts | 
| **Telephone numbers** | Any phone or fax numbers | No | |
| **Fax numbers** | Same as above | No | |
| **Email addresses** | All email addresses | No | |
| **Social Security numbers** | Government-issued personal numbers | No | |
| **Medical record numbers** | Patient record or study IDs | Patient record ID, Clinical center name | String Redaction |
| **Health plan beneficiary numbers** | Insurance or benefit IDs | No | |
| **Account numbers** | Billing or financial identifiers | No | |
| **Certificate/license numbers** | Professional or legal license IDs |No | |
| **Vehicle identifiers and serial numbers** | License plate, VIN |No | |
| **Device identifiers and serial numbers** | Implanted medical device IDs | No | |
| **Web URLs** | Personal or institution-specific links | No | |
| **IP addresses** | Device or network addresses | No | |
| **Biometric identifiers** | Fingerprints, voice prints | No | |
| **Full-face photographs and images** | Identifiable images | No | |
| **Any other unique identifying number, characteristic, or code** | Any indirect identifier | Age, Age at diagnosis | Age Binning |




- **Random Date Shifts:**  
  All date fields (e.g., diagnosis dates, treatment dates) are shifted by a randomly generated number of days unique to each patient, while preserving internal date intervals and sequences.

- **Age Binning:**  
  Patient age is converted into predefined age ranges or bins (e.g., `>20`, `30-34`, `90+`, etc.) instead of displaying exact ages or birthdates.

- **String Redaction:**  
  Free-text fields and identifiable string data (e.g., clinical identifiers) are automatically redacted or replaced with placeholder values like `******` where appropriate.

---

## Access Levels and Data Protection Policies

POP enforces **role-based access control (RBAC)** to manage who can access pseudonymized or anonymized data:

| Access Level | User Role          | Pseudonymized Data | Anonymized Data |
|:-------------:|:------------------|:---------------------------:|:--------------------------:|
| 6 | **Administrator**         | ✅      | ✅                         |
| 5 | **Platform Manager**      | ✅      | ✅                         |
| 4 | **Project Manager**       | ✅      | ✅                         |
| 1 | **Member**                | ✱       | ✱                         |
| 0 | **External**              | ❌      | ❌                         |

✱ *Members* that belong to an *ongoing* research project **can be granted temporary rights by their project leaders** to manage (add, update and delete) data in addition to the right to see the pseudonymized data of the patient.    

Exporting of any data outside of POP is restricted to high-level users such as *Project Managers* or higher (i.e. users who could otherwise have access to the data, e.g. clinicials, IT administrators, etc.).    

## Legal and Ethical Considerations

When handling sensitive data through POP:

- Ensure all data use complies with the applicable **data protection regulations (GDPR, HIPAA)**.
- Secure appropriate **ethics board approvals and data sharing agreements** before accessing pseudonymized datasets or using any data for research purposes.
- Periodically review anonymization and data protection configurations to remain compliant with evolving regulations.

---

## Further Reading

- [User Roles and Permissions](permissions.md)
- [GDPR Official Website](https://gdpr.eu/)
- [HIPAA Security Rule Summary](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html)
