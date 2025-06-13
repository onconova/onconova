
## What is an API?

An **API (Application Programming Interface)** is a set of rules and protocols that allow different software systems to communicate with each other. 

In simpler terms:

- **For non-technical users:** Think of it like a waiter in a restaurant. You (the user) tell the waiter (API) what you want, the waiter takes your request to the kitchen (the server/database), and then brings the result back to you.
- **In POP:** The API allows external systems, scripts, or applications to securely interact with the POP database — retrieving information or submitting new data — without directly accessing the database itself.

APIs are commonly used to:

- **Fetch information** (like patient records or clinical records)
- **Create new entries** (like adding a new patient or a new treatment)
- **Update existing records**
- **Delete data** (with appropriate permissions)

## Purpose

The POP API serves as a controlled gateway for interacting with the POP platform’s database. It enables in a controlled and supervised manner to users and integrated applications to:

- **Query data sources** and obtain both raw and aggregated clinical and genomic data
- **Create new records** within the system such as patients, reports, or terminology entries
- **Retrieve aggregated insights** from processed data sets
- **Integrate third-party clinical systems** or research tools with POP, enabling seamless data exchange without compromising security or data integrity

This is particularly useful for:

- Electronic Health Record (EHR) integrations
- Microservice integrations
- Research data extraction pipelines
- Terminology synchronization tools

## Specification

The API is specified according to the **OpenAPI 3.1 standard**..  All endpoints, parameters, request/response formats, and data schemas are documented and interactively available through this live documentation interface.
A static reference version is also available in the [API Specification](specification.md) section of this documentation.

By adhering to the OpenAPI 3.1 standard, POP provides a formal, machine-readable definition of the API structure. This enables a wide range of tools and workflows for integrators, developers, and analysts:
You can automatically generate fully functional, typed client libraries in a variety of programming languages using OpenAPI code generation tools such as:

- **[OpenAPI Generator](https://openapi-generator.tech/)**
- **Swagger Codegen**
- **Stoplight Studio**
- **Postman (for importing and testing)**

Supported languages and frameworks include:
- Python (e.g. `python-requests`, `pydantic`, `fastapi-clients`)
- JavaScript / TypeScript (e.g. `axios`, `fetch` clients)
- Java, C#, Go, Ruby, and others

This allows developers to:
- Avoid manual implementation of API requests and models.
- Automatically enforce request/response validation and typing.
- Stay synchronized with evolving API schemas through regeneration.

## Authentication

To maintain security and confidentiality, all API requests must be authenticated.
POP uses a **session-based token authentication** mechanism. This means you must include a valid session token in your API requests' headers.

**How to Authenticate**

1. Obtain a session token by logging in through the web interface or by using the API login endpoint:
    ```
    POST /api/auth/login/
    ```

    Example JSON body:
    ```json
    {
        "username": "admin",
        "password": "your_password"
    }
    ```

    Example response:
    ```json
    {
        "session_token": "eyJ0eXAiOiJKV1QiLCJh..."
    }
    ```

2. Include this token in the `X-SESSION-TOKEN` header in your subsequent API requests.

    Example Request with Token:
    ```bash
    curl -X GET "https://pop.example.com/api/patients/" \
        -H "X-SESSION-TOKEN: eyJ0eXAiOiJKV1QiLCJh..."
    ```
!!! note "Token Expiration"
    
    Tokens are valid for a limited period or until manually revoked. After the expriration period, users must authenticate again to retrieve a new token.

!!! warning "Security Considerations"

    - Always keep your session tokens secure.
    - Never expose API credentials or tokens in public code repositories.
    - Use HTTPS connections for all API calls. HTTP connections will be redirected to HTTPS by default.

## API Generation, Versioning, and Implications for Integrators

The POP API is **automatically generated from the database schema** using the server’s schema introspection capabilities. However, to maintain stability and support external integrations, the API is exposed through **explicit, versioned endpoints**. 

The POP API follows a **semantic versioning strategy** with clearly defined major, minor, and patch versions:
```
/api/v1/
```

- `v1` indicates the current major API version.
- Changes to the database schema are mapped to versioned API changes based on their impact:
  - **Non-breaking additions** (e.g., new optional fields, new endpoints) are applied to the current version.
  - **Breaking changes** (e.g., removing fields, changing required parameters, altering response structures) trigger the release of a **new major API version** (e.g., `v2`).

This ensures that:
- Existing integrations targeting `/api/v1/` remain stable and functional, even as the underlying database evolves.
- Integrators can migrate to newer API versions on their own schedule, without being forced to update immediately.

!!! important 

    Each API version maintains its own documentation and endpoint namespace.

#### Implications for Consumers and Integrators

Advantages

- **Stability through Versioning:** Integrations built against a specific API version (e.g. `/api/v1/`) remain compatible, even as new schema changes or features are introduced in `/api/v2/`.
- **Up-to-date Documentation:** Every API version maintains its own interactive documentation at `/api/vX/docs/`, reflecting the state of that version.
- **Predictable Upgrade Path:** Breaking changes are confined to new major versions, so integrators can plan migrations when ready.

Considerations

- **Deprecation Policy:** Older API versions may be deprecated and removed after a defined support period. Integrators should monitor release notes for deprecation notices.
- **Version-Specific Behavior:** Behavior, response formats, and available fields may differ between API versions. Integrators should consult the documentation for their target version.
- **Migration Planning:** Major API updates will require integrators to review changelogs, test applications against new versions, and adapt to any breaking changes.

#### Best Practices for Integrators

- Always **target a specific API version** in your integrations.
- Regularly check the `/api/vX/docs/` endpoint for your version’s specification and updates.
- Subscribe to POP system release notes for notifications about new versions or deprecations.
- Plan for integration testing whenever migrating to a newer API version.
- Avoid hardcoding assumptions about optional fields or undocumented behavior.
