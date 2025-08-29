# Certificates Directory

This folder serves as the **default build context for SSL certificates** during the build and startup phase of Onconova containers. All certificate files required for secure communication should be placed here, unless otherwise specified.

## Purpose

The `/certificates` directory is used to store all SSL-related certificates that the containerized applications may require. By default, the Onconova container build and runtime processes will look for certificate files in this directory to enable secure HTTPS/TLS communication and authentication.

## What to Place Here

You should place the following types of files in this folder:

- **Host SSL certificates**  
  Private and public key files associated with the host or service. These are used to authenticate the container to external clients or services.

- **Root CA certificates**  
  Certificate Authority (CA) files that are required for verifying the identity of remote hosts and SSL endpoints your application communicates with.

> **Note:** Ensure that certificates and keys are stored securely. Avoid committing sensitive private keys to version control.

## Custom Certificate Path

If you need to use a different certificate directory, you can override the default location by setting the following environment variable:

```bash
ONCONOVA_CERTIFICATES_PATH=/path/to/your/certificates
```

When `ONCONOVA_CERTIFICATES_PATH` is set, the container will retrieve SSL certificates from the specified path instead of the default `/certificates` directory.

## Usage Example

1. Place your certificate files (e.g., `server.crt`, `server.key`, `rootCA.pem`) into the `/certificates` folder.
2. Build and run the Onconova container. The certificates will be automatically detected and used for secure operations.
3. If using a custom path, set the `ONCONOVA_CERTIFICATES_PATH` environment variable to the desired directory before starting the container.

## Troubleshooting

- If the container fails to start due to missing certificates, verify that all required files are present in the `/certificates` directory or the custom path specified by `ONCONOVA_CERTIFICATES_PATH`.
- Check file permissions to ensure the container runtime user has appropriate access.
