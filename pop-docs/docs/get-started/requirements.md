## Minimum Hardware and Software Requirements

This document outlines the minimum and recommended hardware, software, and network requirements for deploying and running the POP containerized application stack. These recommendations are based on empirical resource usage observed in a development environment and are intended to help you provision resources effectively for both development and production scenarios.

## System Requirements

The table below summarizes the core system and infrastructure requirements needed to run POP reliably:

| Resource      | Minimum requirements  | 
| -------------- | --------------- | 
| Database      | PostgreSQL 13+  | 
| Docker Engine	| 17.05.0+  |
| Docker Compose | 1.18.0+ |
| CPU | 2 vCPUs	|
| RAM | 3 GB | 
| Storage | 5 GB |

--- 

#### Operating System
POP runs on any system where [Docker](https://www.docker.com/) is supported, including Linux, macOS, and Windows, as well as container platforms such as Docker Compose or Kubernetes.

--- 

#### Database

POP uses **PostgreSQL 13 or later** as its database backend. You can either connect to an existing PostgreSQL instance or deploy a new instance using the provided Docker image.  

**Important:** Due to PostgreSQL-specific functionality within POP, no other database backends (e.g. MySQL, MSSQL, SQLite, Oracle) are supported or compatible.

--- 

#### Network 

The POP container stack includes an NGINX reverse proxy that exposes HTTP and HTTPS ports for client access.  
To secure access to the platform, you must configure:

- Valid SSL/TLS certificates (self-signed or CA-issued)
- Accessible host domain and HTTPS port open to end users

Ensure firewall and network configurations permit traffic on the designated HTTP and HTTPS ports.

--- 

#### CPU & Memory

While POP can technically run on a single CPU core, for stable performance and to leverage multi-worker concurrency in the WSGI server, a minimum of **2 vCPUs** is recommended.

Memory requirements:

  - **Linux systems:** At least **3 GB RAM**
  - **macOS and Windows:** May require slightly more due to higher system overhead

For production deployments, consider provisioning **4 GB or more** for improved performance and resource headroom.

--- 

#### Storage

Storage needs depend on your deployment size and expected data volume.  

- **Database storage:**  
    - Less than **100 MB** for core platform data (terminologies, users, etc.)
    - Approx. **200 KB per patient case** for additional clinical data  
        *Example:* 2,500 cases ≈ 500 MB database storage

- **Container images and logs:**  
    - POP Docker images require approximately **3.5 GB**
    - Minimum recommended storage: **5–10 GB** initially, with scaling as data grows

Consider using SSD storage for improved performance, especially for database operations.

--- 

#### Supported Browsers

POP is a web-based platform accessed via modern browsers. The following browsers are officially supported:

- Google Chrome
- Brave
- Mozilla Firefox
- Microsoft Edge
- Apple Safari

Only the **latest stable versions** of these browsers are supported. Browsers should be configured for automatic updates to maintain compatibility and security.
