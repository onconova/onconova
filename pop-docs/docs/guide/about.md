# Project Overview

The Precision Oncology Platform (POP) is an open-source software project initially developed at the Univserity Hospital of Zurich designed to support data-driven precision oncology research. It provides a secure, structured, and scalable framework for capturing clinical data from oncology patients, while enabling users to explore and analyze aggregated data through an interactive web interface.

## Goals 

The primary aim of POP is to simplify and help standardize how clinical oncology data is collected, organized, and analyzed. By offering an open-source, containerized platform, POP allows institutions and research teams to:

- Capture structured clinical data from oncology patient records.
- Aggregate and analyze data interactively through a modern web interface.
- Facilitate cohort-building and outcome studies based on real-world data.
- Support precision medicine initiatives by surfacing actionable insights from clinical practice data.

## How It Works
POP consists of two main components:

- A Django-based API server that manages clinical data models, authentication, and API endpoints.
- An Angular web client that provides interactive data entry, cohort selection, and data visualization tools.

Both components are containerized using Docker and orchestrated via Docker Compose, making deployment flexible and reproducible across local and production environments.

## Why Open Source?
We believe that the future of precision oncology depends on collaborative, interoperable, and transparent tools. By releasing POP as an open-source project, we aim to:

- Accelerate clinical research innovation.
- Enable reproducible, multi-institutional studies.
- Lower the barriers for healthcare organizations to adopt precision oncology data infrastructure.

Foster a community of contributors to improve and extend the platform.

## Architecture

This section describes the high-level architecture of the POP platform, including its core components, optional extensions, and the way users and services interact.

```mermaid
flowchart RL
    subgraph "Core" 
        server[POP server]
        client[POP client]
        db[(POP Database)]
    api[POP API] 
    end
    user[User]
    subgraph "Customization (optional)" 
        microservices@{ shape: processes, label: "Microservices" }
        plugins@{ shape: processes, label: "Client Plugins" }
    end

    user <--> client

    client <-----> api
    server <---> api
    db <--> server

    microservices <.-> api
    plugins <.-> client
    plugins <.-> microservices
```

#### Core Components

- **POP Server** - The backend service responsible for handling business logic, API processing, and database interactions. It exposes the POP API to facilitate communication with the client and optional microservices.
- **POP Client** - A frontend application, a single-page application (SPA), that provides the user interface. It communicates with the POP API to fetch or send data and display dynamic content to the user.
- **POP API** - An API layer that acts as the communication bridge between the client and the server. It provides endpoints for retrieving data, submitting forms, managing user actions, and invoking server-side business logic.
- **POP Database** - A relational database responsible for persistent data storage. It is accessed by the POP Server to read and write application data.

#### Customization Components

- **Microservices** - Independent, decoupled services that can extend or augment the core API functionality. These may handle specific business domains, integrations, or asynchronous processes. They communicate bidirectionally with the **POP API** and, optionally, with **Client Plugins**.
- **Client Plugins** - Custom client-side extensions or modules that enhance or modify the behavior of the POP Client. These plugins can also interact directly with microservices for advanced client-side features like live data feeds, third-party integrations, or UI customizations.

## Component Orchestration

This architecture represents a web-based platform composed of multiple interconnected services orchestrated within Docker containers, centered around an Nginx reverse proxy.

```mermaid
graph TD
    user@{ shape: sm-circ, label: "" }   
    subgraph pop-nginx [pop-nginx]
        nginx[Host Machine Nginx Reverse Proxy]
    end

    client-nginx[Client Nginx Server]
    docs-nginx[Docs Nginx Server]
    docs@{ shape: win-pane, label: "Documentation HTML Files" }
    client@{ shape: win-pane, label: "Client JS Files" }
    gunicorn[Gunicorn WSGI Server]
    workers@{ shape: processes, label: "Django workers" }
    
    subgraph pop-postgres [pop-postgres]
        postgres[(PostgreSQL Database)]
    end

    %% Connections
    user -- HTTPS Requests --> nginx
    nginx -- Redirect HTTP @ / --> client-nginx
    nginx -- Redirect HTTP @ /api --> gunicorn
    nginx -- Redirect HTTP @ /docs --> docs-nginx
    
    subgraph pop-client [pop-client]
    client-nginx --> client
    end
    
    subgraph pop-docs [pop-docs]
    docs-nginx --> docs
    end

    subgraph pop-server [pop-server]
    gunicorn --> workers
    workers --> postgres
    end
```

User Interaction

- A user initiates an HTTPS request from their browser or API client.
- The request first reaches the Host Machine’s Nginx Reverse Proxy (`pop-reverse-proxy`).


Nginx Reverse Proxy (`pop-reverse-proxy`)

- Acts as a secure entry point for all incoming HTTPS traffic.
- Based on the URL path of the request, Nginx routes the traffic to one of three destinations:

   + `/` → the Client Application (`pop-client`).
   + `/api` → the API service (`pop-server`).
   + `/docs` → the Documentation service (`pop-docs`).

Client Application (`pop-client`)

- Requests sent to `/` are proxied to a Client Nginx Server running within the `pop-client` container.
- This server serves static frontend assets like JavaScript, CSS, and HTML files for the single-page application (SPA).
- The actual application files reside in a directory labeled Client JS Files in the diagram.

Documentation Service (`pop-docs`)

- Requests sent to `/docs` are forwarded to a Docs Nginx Server inside the `pop-docs` container.
- This Nginx server serves static documentation assets, represented as Documentation HTML Files.

API Service (`pop-server`)

- Requests sent to `/api` are proxied to the Gunicorn WSGI Server within the `pop-server` container.
- Gunicorn handles these requests by distributing them to multiple Django worker processes.
- Each worker runs a Django application instance capable of processing API requests.

PostgreSQL Database (`pop-database`)

- All database queries generated by the Django workers are sent to a PostgreSQL database hosted in the `pop-database` container.
- The PostgreSQL instance serves as the primary relational database for persisting and retrieving application data.