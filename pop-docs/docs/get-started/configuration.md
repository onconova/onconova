
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

| Variable                          | Description |
|:----------------------------------|:------------|
| `COMPOSE_FILE`                    | Specifies which Docker Compose file to use (development or production). |
| `HOST_SSL_CERTIFICATE_BUNDLE`     | Path to the SSL certificate bundle for the host. |
| `HOST_SSL_CERTIFICATE_PRIVATE_KEY`| Path to the SSL private key for the host. |
| `WEBAPP_HOST`                     | Domain or hostname where the POP web application will be served. |
| `WEBAPP_HTTPS_PORT`               | External HTTPS port for POP web application connections. |
| `WEBAPP_HTTP_PORT`                | External HTTP port for POP web application connections. |
| `ORGANIZATION_NAME`               | Name of the organization or healthcare provider deploying POP. |
| `ANONYMIZATION_SECRET_KEY`        | Secret key for anonymizing protected healthcare information (PHI). |
| `DJANGO_SECRET_KEY`               | Secret key used by Django to cryptographically sign sensitive data. |
| `DJANGO_ALLOWED_HOSTS`            | Comma-separated list of allowed hosts to serve the POP server. Typically matches `WEBAPP_HOST`. |
| `EXTERNAL_DATA_DIR`               | Path within the server container for temporary files used by terminology connectors. |
| `POSTGRES_DATABASE`               | Name of the PostgreSQL database for POP. |
| `POSTGRES_USER`                   | PostgreSQL admin username for POP. |
| `POSTGRES_PASSWORD`               | Password for the PostgreSQL database user. |
| `POSTGRES_HOST`                   | Hostname of the PostgreSQL database server. |
| `POSTGRES_PORT`                   | Exposed port of the PostgreSQL database server. |
| `CLIENT_PLUGINS_PATH` *(optional)*  | Path to directory containing POP client plugins to install on service start. |
| `POP_GOOGLE_CLIENT_ID` *(optional)* | Google OIDC client ID for SSO. |
| `POP_GOOGLE_SECRET` *(optional)*    | Google OIDC secret for SSO. |
| `POP_MICROSOFT_CLIENT_ID` *(optional)* | Microsoft OIDC client ID for SSO. |
| `POP_MICROSOFT_TENANT_ID` *(optional)* | Microsoft OIDC client secret for SSO. |
| `POP_MICROSOFT_SECRET` *(optional)* | Microsoft OIDC tenant ID for SSO. |

Be sure to update environment variable values according to your deployment infrastructure and security requirements before starting the application.