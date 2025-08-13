
## Environment Variables

Environment variables are a fundamental part of configuring modern applications, allowing you to manage settings and sensitive credentials separately from your application code. In the POP platform, environment variables control essential runtime configurations for both the Django backend and Docker services, enabling flexible, secure, and environment-specific deployments without requiring code changes.

!!! tip "Why Use Environment Variables?"

    - Keep sensitive information (like API keys and database credentials) **out of the codebase**.
    - Easily switch configurations between **different environments**.
    - Simplify **deployment automation and container orchestration** workflows.
    - Improve security by centralizing the management of sensitive values.

#### Creating a New  `.env` for Local Deployment

To get started locally, copy the provided `.env.template` file to create your working `.env` file:

```shell
mv .env.template .env
```

Then, open the `.env` file and fill in the necessary environment variables according to your environment and preferences. This file is automatically loaded by Docker Compose when starting services.

!!! warning "Security Notice"

    - **Never commit `.env` files with sensitive values** to your git repository.
    - Ensure `.env` is listed in your `.gitignore` file to avoid accidental exposure.


#### Environment Variables in Production

In production environments (e.g., on a cloud server or container orchestration platform like Kubernetes), you should set environment variables securely through the deployment environment itself.

- Use a secret management system (e.g., Docker secrets, AWS SSM Parameter Store, Vault) for sensitive values.
- Export variables in your system shell before starting the services.
- Use a production-specific `.env` file.

### POP Environment Variables Reference

The following variables control the different configurable aspects of the POP components.

| Variable                                         | Description |
|:------------------------------------------------|:------------|
| `COMPOSE_FILE`                                  | Specifies which Docker Compose file to use (`compose.dev.yml` or `compose.prod.yml`). |
| `POP_HOSTING_ORGANIZATION`                      | Name of the organization or healthcare provider deploying POP. |
| `POP_REVERSE_PROXY_HOST`                        | Hostname or IP address of the server hosting the POP reverse proxy. |
| `POP_REVERSE_PROXY_HTTPS_PORT`                  | HTTPS port exposed by the POP reverse proxy. |
| `POP_REVERSE_PROXY_HTTP_PORT`                   | HTTP port exposed by the POP reverse proxy. |
| `POP_REVERSE_PROXY_SSL_CERTIFICATE_BUNDLE`      | Path to the SSL certificate bundle for the reverse proxy. |
| `POP_REVERSE_PROXY_SSL_CERTIFICATE_PRIVATE_KEY` | Path to the SSL private key for the reverse proxy. |
| `POP_SERVER_ADDRESS` *(optional)*               | Address (`host:port`) of the POP server. Defaults to the reverse proxy address if unset. |
| `POP_SERVER_ANONYMIZATION_KEY`                  | Secret key for anonymizing protected healthcare information (PHI). |
| `POP_SERVER_ENCRYPTION_KEY`                     | Secret key used by the server to cryptographically sign sensitive user data. |
| `POP_SERVER_ALLOWED_HOSTS`                      | Comma-separated list of allowed `HOST` headers for incoming requests to the server. |
| `POP_SERVER_CORS_ALLOWED_ORIGINS`               | Comma-separated list of allowed CORS origins (used for AJAX requests). |
| `POP_CLIENT_WEBSERVER_ADDRESS` *(optional)*     | Address (`host:port`) of the POP client webserver. Defaults to the reverse proxy address if unset. |
| `POP_CLIENT_PLUGINS_PATH` *(optional)*          | Path to the directory containing client-side plugin source code. |
| `POP_DOCS_WEBSERVER_ADDRESS` *(optional)*       | Address (`host:port`) of the documentation server. Defaults to the reverse proxy address if unset. |
| `POP_SNOMED_ZIPFILE_PATH`                       | Path to the SNOMED terminology ZIP file used by the terminology connector. |
| `POP_GOOGLE_CLIENT_ID` *(optional)*             | Google OIDC client ID for Single Sign-On (SSO). |
| `POP_GOOGLE_SECRET` *(optional)*                | Google OIDC secret key for Single Sign-On (SSO). |
| `POP_MICROSOFT_CLIENT_ID` *(optional)*          | Microsoft OIDC client ID for Single Sign-On (SSO). |
| `POP_MICROSOFT_TENANT_ID` *(optional)*          | Microsoft OIDC tenant ID for Single Sign-On (SSO). |
| `POP_MICROSOFT_SECRET` *(optional)*             | Microsoft OIDC secret key for Single Sign-On (SSO). |
| `POP_POSTGRES_DATABASE`                             | Name of the PostgreSQL database used by POP. |
| `POP_POSTGRES_USER`                                 | Username for the PostgreSQL database user. |
| `POP_POSTGRES_PASSWORD`                             | Password for the PostgreSQL database user. |
| `POP_POSTGRES_HOST`                                 | Hostname or container name of the PostgreSQL server. |
| `POP_POSTGRES_PORT`                                 | Port exposed by the PostgreSQL server. |


Be sure to update environment variable values according to your deployment infrastructure and security requirements before starting the application.