---
hide:
  - toc
  - navigation
---

Below are answers to common questions about installing, configuring, and using the Precision Oncology Platform (POP). If your question isn't listed here, feel free to check the Issues page or GitHub Discussions.


#### Is POP free to use?
Yes — POP is released as an open-source project under the MIT License. You are free to use, modify, and distribute it under the terms of this license.

--- 


#### Is POP production-ready?
Yes, POP is designed for production environments. However, you should carefully review the security, compliance, and data handling features before deploying in a clinical or regulated setting.

--- 


#### Does POP support Single Sign-On (SSO)?
Yes — POP integrates with the Django-AllAuth authentication framework and provides built-in SSO support for Google and Microsoft. See the [Authentication guide](guide/security/authentication.md) for integration instructions.

--- 


#### Can I export data from POP for my research?
Yes — users with sufficient access (typically Project Managers or higher) can export anonymized or pseudonymized patient case data, depending on their access level and project permissions. See [Access Control](guide/security/permissions.md) for details.

--- 

#### Is patient data anonymized?
POP uses an annymization system where data fields are treated according to the "Safe-Harbor" method of the HIPAA rules. Detailed information can be found in the [Data Security](guide/security/data-security.md) section.

--- 

#### Why cannot I create any new cohorts?
Cohort creation is limited to the scope of research projects. If you are not a member of a project you cannot create or edit cohorts.

--- 


#### Do I need an ethics approval to use this platform for a research project?
Yes — if your use of the Precision Oncology Platform (POP) involves handling clinical data, even in anonymized or pseudonymized form, you are typically required to obtain approval from your institution’s ethics committee or institutional review board (IRB) before starting your research project.

While POP provides technical safeguards for data protection and privacy, ethical oversight is essential to:

- Ensure the research complies with local, national, and international data protection regulations (such as GDPR or HIPAA).
- Protect the rights and privacy of patients whose data is being processed.
- Review and authorize the intended scope of data use, sharing, and analysis.

!!! important

    Obtaining ethics approval is the responsibility of the research team or data owner. The POP platform itself does not grant or manage ethics approvals but is designed to support compliance through access controls, audit trails, and data anonymization features.

    If in doubt, consult your institution’s data protection officer or ethics committee before beginning a project on POP.

--- 


#### Can I share exported data from POP with external collaborators?
Technically, yes — POP’s data export functionality is designed to produce interoperable, standards-compliant data that can be easily shared between institutions or research partners.

However, whether you may share exported data depends entirely on your ethics approval, institutional policies, and data protection regulations:

- Ethics approval and institutional authorization must explicitly permit data sharing for your specific research project.
- Any data sharing agreement should define the permitted scope of use, data security measures, and handling procedures for exported data.
- Even anonymized or pseudonymized data should be treated cautiously, especially if there’s a risk of re-identification through dataset combination.

--- 


#### Do I need patient consent to include their data in POP?
Yes. Before patient data can be included in POP — whether for clinical documentation, research, or data analysis — appropriate patient consent must be obtained in accordance with local laws, institutional policies, and ethical guidelines.

Important considerations:

- It is the responsibility of the project leader to ensure that valid, current patient consents are in place for all cases included in a cohort or research project.
- For existing or legacy patient cases, consents must be reviewed and verified as still valid and applicable to the intended research use.
- Ethics approval documentation should reflect the consent procedures and scope of data usage for the project.

Note: Failure to obtain or verify proper consent before using data for research may constitute a serious ethical and legal violation.

--- 

