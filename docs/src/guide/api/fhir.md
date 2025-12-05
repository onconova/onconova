# FHIR Interface

## Overview

In addition to the traditional REST API, Onconova provides a **FHIR (Fast Healthcare Interoperability Resources) interface** that enables standards-based healthcare data exchange. This interface offers an alternative interoperability approach specifically designed for integration with healthcare systems, Electronic Health Records (EHRs), and other FHIR-compliant applications.

The FHIR interface exposes Onconova's clinical data using internationally recognized healthcare data standards, making it easier for healthcare institutions to integrate with existing infrastructure while maintaining semantic interoperability.

## What is FHIR?

**FHIR (Fast Healthcare Interoperability Resources)** is a modern healthcare data exchange standard developed by HL7 International. It provides:

- **Standardized data models** for healthcare resources (Patient, Observation, Condition, etc.)
- **RESTful APIs** for creating, reading, updating, and deleting healthcare data
- **Interoperability** between different healthcare systems and applications
- **Clinical terminology support** using standard code systems like SNOMED CT, LOINC, and ICD-10

## FHIR Implementation Guide

Onconova's FHIR interface is fully documented in its **Implementation Guide (IG)**, which provides:

- **Resource profiles** defining how standard FHIR resources are used in Onconova
- **API endpoints** and interaction patterns
- **Data mappings** between Onconova's internal data model and FHIR resources
- **Usage examples** and integration guidance
- **Validation rules** and conformance requirements

📖 **[Access the complete FHIR Implementation Guide →](https://onconova.github.io/fhir/)**

The Implementation Guide is the authoritative source for all FHIR-related technical details, including:

- Cancer-specific resource profiles
- Terminology bindings and code systems
- Search parameters and capabilities
- Conformance requirements and validation rules

## Key Differences from REST API

| Feature | REST API | FHIR Interface |
|---------|----------|----------------|
| **Data Format** | Custom JSON schemas | FHIR-compliant resources |
| **Standards Compliance** | Onconova-specific | HL7 FHIR R4 & mCODE |
| **Target Users** | General integrations | Healthcare systems |
| **Data Anonymization** | Fully anonymized | Pseudonymized (elevated access) |
| **Authentication** | Session tokens | Session tokens |
| **Use Cases** | Research, analytics | EHR integration, data exchange |

## Security and Access Control

The FHIR interface operates with different security considerations compared to the standard REST API:

### Authentication

FHIR API endpoints use the same session-based authentication as the REST API but require additional permissions:

```bash
# Example authenticated FHIR request
curl -X GET "https://onconova.example.com/fhir/Patient" \
    -H "X-SESSION-TOKEN: eyJ0eXAiOiJKV1QiLCJh..." \
    -H "Accept: application/fhir+json"
```

## Getting Started

1. **Review the Implementation Guide**: Start with the [FHIR IG](https://onconova.github.io/fhir/) to understand available resources and profiles

2. **Obtain elevated permissions**: Contact your system administrator to request FHIR interface access

3. **Authentication setup**: Use the same authentication mechanism as the REST API, ensuring your user account has appropriate permissions

4. **Test integration**: Begin with read-only operations to familiarize yourself with the data model

5. **Implement error handling**: Follow FHIR standards for error responses and operation outcomes

## Compliance and Standards

Onconova's FHIR interface is designed to support:

- **HL7 FHIR R4** specification compliance
- **US Core** profiles where applicable
- **International Patient Summary (IPS)** for global interoperability
- **SMART on FHIR** for application integration (planned)

