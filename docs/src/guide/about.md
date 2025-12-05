# Project Overview

Onconova is an open-source software project initially developed at the Univserity Hospital of Zurich designed to support data-driven precision oncology research. It provides a secure, structured, and scalable framework for capturing clinical data from oncology patients, while enabling users to explore and analyze aggregated data through an interactive web interface.

## Goals 

The primary aim of Onconova is to simplify and help standardize how clinical oncology data is collected, organized, and analyzed. By offering an open-source, containerized platform, Onconova allows institutions and research teams to:

- Capture structured clinical data from oncology patient records.
- Aggregate and analyze data interactively through a modern web interface.
- Facilitate cohort-building and outcome studies based on real-world data.
- Support precision medicine initiatives by surfacing actionable insights from clinical practice data.
- Enable FHIR-compliant interoperability with external healthcare systems and Electronic Health Records (EHRs).

## How It Works
Onconova consists of two main components:

- A Django-based API server that manages clinical data models, authentication, and API endpoints.
- An Angular web client that provides interactive data entry, cohort selection, and data visualization tools.
- A FHIR-compliant interoperability interface that enables standards-based data exchange with external healthcare systems.

Both components are containerized using Docker and orchestrated via Docker Compose, making deployment flexible and reproducible across local and production environments.

## Why Open Source?
We believe that the future of precision oncology depends on collaborative, interoperable, and transparent tools. By releasing Onconova as an open-source project, we aim to:

- Accelerate clinical research innovation.
- Enable reproducible, multi-institutional studies.
- Lower the barriers for healthcare organizations to adopt precision oncology data infrastructure.

Foster a community of contributors to improve and extend the platform.

## Architecture

This section describes the high-level architecture of the Onconova platform, including its core components, optional extensions, and the way users and services interact.

```mermaid
flowchart RL
    subgraph "Core" 
        server[Onconova server]
        client[Onconova client]
        db[(Onconova Database)]
        api[Onconova REST API] 
        fhir[Onconova FHIR Interface]
    end
    user[User]
    healthcare[Healthcare Systems]
    subgraph "Customization (optional)" 
        microservices@{ shape: processes, label: "Microservices" }
        plugins@{ shape: processes, label: "Client Plugins" }
    end

    user <--> client
    healthcare <--> fhir

    client <-----> api
    server <---> api
    server <---> fhir
    db <--> server

    microservices <.-> api
    microservices <.-> fhir
    plugins <.-> client
    plugins <.-> microservices
```

#### Core Components

- **Onconova Server** - The backend service responsible for handling business logic, API processing, and database interactions. It exposes both the REST API and FHIR interface to facilitate communication with clients, healthcare systems, and optional microservices.
- **Onconova Client** - A frontend application, a single-page application (SPA), that provides the user interface. It communicates with the Onconova REST API to fetch or send data and display dynamic content to the user.
- **Onconova REST API** - An API layer that provides endpoints for research and analytical workflows. It serves anonymized data and supports general application integration, data retrieval, form submission, and server-side business logic.
- **FHIR Interface** - A standards-compliant FHIR API that enables healthcare system integration. It provides pseudonymized data access for authorized clinical workflows and supports HL7 FHIR R4 resource interactions.
- **Onconova Database** - A relational database responsible for persistent data storage. It is accessed by the Onconova Server to read and write application data for both API interfaces.

#### Customization Components

- **Microservices** - Independent, decoupled services that can extend or augment the core functionality. These may handle specific business domains, integrations, or asynchronous processes. They can communicate bidirectionally with both the **Onconova REST API** and **FHIR Interface**, as well as optionally with **Client Plugins**.
- **Client Plugins** - Custom client-side extensions or modules that enhance or modify the behavior of the Onconova Client. These plugins can also interact directly with microservices for advanced client-side features like live data feeds, third-party integrations, or UI customizations.

## Component Orchestration

This architecture represents a web-based platform composed of multiple interconnected services orchestrated within Docker containers, centered around an Nginx reverse proxy.

```mermaid
graph TD
    user@{ shape: sm-circ, label: "" }   
    subgraph onconova-nginx [reverse-proxy]
        nginx[Host Nginx Reverse Proxy]
    end

    client-nginx[Client Nginx Server]
    client@{ shape: win-pane, label: "Client JS Files" }
    gunicorn[Gunicorn WSGI Server]
    workers@{ shape: processes, label: "Django workers" }
    
    subgraph onconova-postgres [postgres]
        postgres[(PostgreSQL Database)]
    end

    %% Connections
    user -- HTTPS Requests --> nginx
    nginx -- Redirect HTTP @ / --> client-nginx
    nginx -- Redirect HTTP @ /api --> gunicorn
    
    subgraph onconova-client [client]
    client-nginx --> client
    end

    subgraph onconova-server [server]
    gunicorn --> workers
    workers --> postgres
    end
```

User Interaction

- A user initiates an HTTPS request from their browser or API client.
- The request first reaches the Host Machine’s Nginx Reverse Proxy (`onconova-reverse-proxy`).


Nginx Reverse Proxy (`reverse-proxy`)

- Acts as a secure entry point for all incoming HTTPS traffic.
- Based on the URL path of the request, Nginx routes the traffic to different destinations:

   + `/` → the Client Application (`client`).
   + `/api/vX` → the REST API service (`server`).
   + `/api/fhir` → the FHIR API service (`server`).

Client Application (`client`)

- Requests sent to `/` are proxied to a Client Nginx Server running within the `client` container.
- This server serves static frontend assets like JavaScript, CSS, and HTML files for the single-page application (SPA).
- The actual application files reside in a directory labeled Client JS Files in the diagram.

API Services (`server`)

- Requests sent to `/api` and `/api/fhir` are proxied to the Gunicorn WSGI Server within the `server` container.
- Gunicorn handles these requests by distributing them to multiple Django worker processes.
- Each worker runs a Django application instance capable of processing both REST API and FHIR interface requests.

PostgreSQL Database (`database`)

- All database queries generated by the Django workers are sent to a PostgreSQL database hosted in the `database` container.
- The PostgreSQL instance serves as the primary relational database for persisting and retrieving application data.