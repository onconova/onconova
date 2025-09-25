---
title: Onconova FHIR Implementation Guide
---

**Onconova** is an open-source precision oncology platform focused on enabling advanced cancer research, clinical decision support, and data-driven care. The FHIR interface exposes key resources, profiles, and value sets to facilitate standardized data exchange and integration with EHRs, registries, and analytics platforms.

This implementation guide provides a comprehensive overview of the FHIR-based server interface to Onconova, supporting interoperability, data exchange, and integration with clinical and research systems. It complements the [OpenAPI specification](https://luisfabib.github.io/onconova/latest/guide/api/specification/) and is designed for healthcare organizations, developers, and integrators seeking to leverage Onconova's oncology data.

This FHIR interface is designed to align with the [**minimal Common Oncology Data Elements (mCODE)** STU4 Implementation Guide](http://hl7.org/fhir/us/mcode/ImplementationGuide/hl7.fhir.us.mcode), leveraging established, community-driven standards for oncology data. The Onconova IG refines and constrains mCODE resources to ensure consistent data elements and terminology bindings. Additionally, it defines new profiles to address oncology use cases not yet covered by the mCODE IG.

---

_Onconova is an open source project and welcomes all contributors. The source code for this IG is maintained in the [Onconova Github](https://github.com/luisfabib/onconova). All of the profiling work is done using FHIR Shorthand and SUSHI. All content is subject to change._