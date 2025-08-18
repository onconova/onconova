The Precision Oncology Platform (POP) is designed to be **modular and institution-agnostic**. To support custom workflows, local system integrations, and specialized processing without compromising the integrity and maintainability of the core platform, POP encourages the use of microservices for all server-side customizations.

This page outlines best practices for developing, integrating, and authenticating microservices within the POP ecosystem.

## What Are POP Microservices?

A POP microservice is a lightweight, standalone service that:

- **Interacts with POP via its public API** for reading or writing data.
- **Optionally exposes its own API** for client-side plugins or external tools to consume.
- **Never interacts directly with the POP database**, all communication must go through the platform’s API to preserve auditability, access control, and data integrity.

## When to Build a Microservice

Use a microservice if you need to:

- Connect POP to an external data source (e.g. an institutional data warehouse or EHR).
- Automate data imports, transformations, or exports.
- Implement institution-specific business logic.
- Provide specialized API endpoints for POP client plugins.
- Schedule or run long-running background processes.

!!! danger 

    Never implement institution-specific or custom server logic directly in the core POP codebase.

## How Microservices Interact with POP

A typical microservice workflow:

1. Authenticate with the POP API using a dedicated technical POP user account.
2. Consume POP API endpoints to read or write clinical, project, or cohort data.
3. Optionally, expose its own lightweight API for the Angular client or external systems to interact with.
4. Respect the same access control rules, data protection standards, and audit policies as any other POP API consumer.

## Utility of OpenAPI Code Generators

To simplify microservice development and reduce boilerplate code when interacting with the POP API, we recommend using OpenAPI client code generators.

+ **Benefits:**

  - Auto-generates Python, Java, TypeScript, or other language clients from the POP API’s OpenAPI specification.
  - Automatically handles API endpoints, authentication headers, data model classes, and request/response validation.
  - Greatly reduces development time and potential for errors.

+ **Recommended Tools:**

    - OpenAPI Generator
    - Swagger Codegen

    *Example:*
    Generate a Python client SDK for the POP API:

    ```
    openapi-generator-cli generate -i https://your-pop-domain/api/schema/swagger.json -g python -o ./pop_api_client
    ```
    This SDK can then be used within your microservice for seamless, typed API interactions.

## Microservice Authentication

Every microservice must use a dedicated technical POP user account to:

- Authenticate with the POP API.
- Ensure data flows and operations performed by the service are traceable and auditable.
- Limit permissions strictly to what the service requires, using the appropriate access level.

How to set it up:

1. Create a user account in POP.
2. Assign the appropriate access level.
3. Use API tokens or OAuth credentials (if configured) for authentication.
4. Log and monitor all API interactions under this user identity.

