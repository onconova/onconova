Thank you for your interest in contributing to the Precision Oncology Platform (POP)! POP is an open-source project that relies on collaboration from the community — developers, clinicians, data scientists, and institutions — to improve and extend its capabilities.

This guide explains how you can propose changes, what types of contributions are welcome, and the processes in place to ensure quality, security, and maintainability.

## Contribution Types

There are two main categories of contributions:

### Core Platform Contributions

Changes that affect the **core functionality of POP** — including backend models, APIs, frontend components, security layers, and shared infrastructure.

Examples:

- Improvements to the data model or API endpoints.
- Enhancements to the authentication system.
- Bug fixes in shared components.
- UI/UX improvements affecting all users.

!!! note 

    Changes to the existing core database models (Django models / schema) must be:

    - Well justified and documented.
    - Submitted via a Pull Request (PR) for review.
    - Approved by the core POP development team.
    - Unless critical or part of a planned roadmap, schema changes should be avoided to preserve platform stability and backwards compatibility.

### Institution-Specific Features

Some features may be tailored for a specific institution, such as:

- Integrating with a local data warehouse.
- Connecting to a proprietary EHR system.
- Adding custom authentication methods.
- Providing institution-specific reporting tools.

In these cases:

- Do not modify the core platform directly.
- Implement the functionality as:
 
    + A client plugin (if it modifies or extends the Angular client).
    + A microservice or standalone service that communicates via the POP API.

This keeps the core platform clean, maintainable, and institution-agnostic while allowing for flexibility and extensibility.

## Development Workflow

1. **Fork the Repository**

    - Create a personal fork of the POP repository on GitHub.

2. **Set Up Your Development Environment**

    - Follow the [Installation Guide](../../get-started/installation.md) to set up POP locally for development using Docker Compose.

3. **Create a Feature Branch**

    - Use descriptive branch names:

        ```
        feature/add-new-api-endpoint
        bugfix/fix-export-error
        plugin/custom-data-importer
        ```

4. **Make Your Changes**

    - Follow the project’s coding standards (Python: PEP8, Angular: ESLint rules).
    - Write clean, readable, and well-documented code.
    - Include clear, well-structured commit messages.
    - If modifying the core database models, document your reasoning clearly in your PR description.
    - Follow existing file structures and naming conventions.
    - Avoid hardcoding institution-specific logic into core components.
    - Use environment variables and configuration files for deploy-time settings.

5. **Test Thoroughly**

    - Run unit tests and integration tests.
    - Add new tests for new functionality.
    - Verify Docker containers build and run cleanly.
    - Test frontend and backend functionality locally.

6. **Submit a Pull Request**

    - Provide a clear, informative description:

        + Purpose of the change.
        + Type of contribution (core change / institution-specific feature).
        + Any model or schema changes proposed, with justification.
        + Testing steps performed.

    - Label the PR appropriately.

### Code Review & Approval
All contributions must be reviewed and approved by a POP core development team member before being merged.

The review process ensures:

- Code quality, consistency, and security.
- Compatibility with existing components.
- Preservation of platform-agnostic design.
- Cmpliance with clinical data protection and ethical principles.

Schema changes, in particular, will receive additional scrutiny and are generally discouraged unless:

- Fixing a critical bug.
- Addressing a necessary compatibility issue.
- Part of an approved roadmap feature.