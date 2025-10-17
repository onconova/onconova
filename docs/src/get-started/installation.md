

The following sections will guide you through the installation and initial configuration of Onconova on a Linux-based machine. 
Make sure that your hardware and network fulfill the [minimal requirements](requirements.md) for installing Onconova.

!!! info "Internet Access"

    The installation and setup of Onconova is the only instance where **an open connection to the Internet** will be required. 
    This is necessary to download the different Onconova components, third-party packages, and other relevant files required for its function.

    For security reasons, **your network may require a proxy configuration and/or root CA certificates to connect to the internet**. 
    If a command requires an active internet connection, you can switch to a tab where the same command with the added configuration for your network will be shown.


### Instructions

Follow these steps to install and set up Onconova from its source code.

1. **Download Required Files**
    
    === "Installing Public Release"

        Download the Docker compose orchestration file from [here](https://raw.githubusercontent.com/onconova/onconova/refs/tags/1.0.0/.env.sample).

    === "Installing From Source"

        Download the Onconova source code and navigate to the project directory:
        ```bash
        git clone https://github.com/onconova/onconova.git
        cd onconova
        ```
   
2. **Setup Host SSL Certificates**

    SSL certificates (i.e `.pem` files) are required to serve the application securely.
        
    === "Local hosting"

        To generate self-signed certificates for local hosting, you can use:

        === "OpenSSL"

            ```shell
            openssl req -x509 -newkey rsa:4096 -keyout localhost-key.pem -out localhost.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=Local/L=Local/O=localhost/OU=localhost/CN=localhost"
            ```

        === "Certbot"

            ```shell 
            sudo certbot certonly --standalone --preferred-challenges http -d localhost
            ``` 
            
            This will generate your certificates, typically at:

            ```
            /etc/letsencrypt/live/localhost/fullchain.pem
            /etc/letsencrypt/live/localhost/privkey.pem
            ```

        Note the path where the certificate and the private key files have been generated for the next step.

    === "Hosting Within an Organization"

        If hosting within a corporate network, contact your IT department to request SSL certificates for the domain where the Onconova instance will be hosted.
        
        Copy the certificates into a local folder and adjust the paths in your `.env` accordingly (see below).

3. **Configure the environment**

    Set up the environment variables to configure the installation for your machine and network:

    === "Installing Public Release"

        - Download the sample environment [here](https://raw.githubusercontent.com/onconova/onconova/refs/tags/1.0.0/compose.yml) and save it under `.env`.

    === "Installing From Source"

        - Copy the provided `.env.sample` to `.env`.
            ```bash
            cp .env.sample .env
            ```

    - Update the `.env` file with your configuration settings:

        - Set the absolute paths to the SSL certificates you obtained or generated in the previous step:
            ```bash
            ONCONOVA_REVERSE_PROXY_SSL_CERTIFICATE_BUNDLE='/path/to/certificate.pem'
            ONCONOVA_REVERSE_PROXY_SSL_CERTIFICATE_PRIVATE_KEY='/path/to/privkey.pem'
            ```

        - Set the correct Docker compose file.
    
            === "Production" 
            
                ```bash
                COMPOSE_FILE=compose.prod.yml 
                ```
                
            === "Development" 
            
                ```bash
                COMPOSE_FILE=compose.dev.yml 
                ```

        - Set all other non-optional environment variables listed in the [Configuration section](configuration.md#onconova-environment-variables-reference) based on your environment.

4. **Start the Containers**

    === "Installing Public Release"

        Start the Onconova containers by running:

        ```bash
        docker compose up -d
        ```

    
    === "Installing From Source"
        Build and start the Onconova containers:

        === "Normal"

            ```bash
            docker compose up --build -d
            ```

        === "With proxy and/or root certificates"

            1. Copy the root CA certificates
                ```bash 
                cp <local-path/root-ca-certificates.pem> ./certificates/root-ca-certificates.pem
                ```

            2. Build the Onconova images:

                ```bash
                docker compose build \
                    --build-arg http_proxy='http://<username>:<password>@<hostname>:<port>' \
                    --build-arg https_proxy='http://<username>:<password>@<hostname>:<port>' \
                    --build-arg ROOT_CA_CERTIFICATES='root-ca-certificates.pem'
                ```
                Replace proxy credentials based on your environment.

            3. Start the containers:

                ```bash
                docker compose up -d
                ```

    Check that the containers are running:
    ```bash
    >>> docker compose ps

    CONTAINER ID   IMAGE                COMMAND                  NAMES
    ************   nginx:1.23           "/docker-entrypoint.…"   onconova-reverse-proxy
    ************   client               "docker-entrypoint.s…"   onconova-client
    ************   server               "python manage.py ru…"   onconova-server
    ************   postgres:13-alpine   "docker-entrypoint.s…"   onconova-database
    ```



5. **Checks**

    To verify that the server and client containers are running and operational, execute the following commands:

    === "Server"

        ```sh
        bash -c 'export $(grep -v "^#" .env | xargs); \
        curl https://${ONCONOVA_REVERSE_PROXY_HOST}:${ONCONOVA_REVERSE_PROXY_HTTPS_PORT}/api/v1/healthcheck \
        --cacert ./certificates/cert.pem -f -o /dev/null;'
        ```

    === "Client"

        ```sh
        bash -c 'export $(grep -v "^#" .env | xargs); \
        curl https://${ONCONOVA_REVERSE_PROXY_HOST}:${ONCONOVA_REVERSE_PROXY_HTTPS_PORT}/login \
        --cacert ./certificates/cert.pem -f -o /dev/null;'
        ```

    If the `curl` command does not raise any errors, then the services are operational. 

!!! important "Follow-up steps"

    If this is a fresh install of Onconova, please proceed to the next section and complete its steps before using the platform any further.


## First-time Setup of the Database

Before using Onconova, the database must be configured and populated with required clinical terminology data.

!!! note "First-time only"

    If you already have a configured and populated Onconova database, you can skip these steps. 

1. **Apply migrations**

    Run the following command to apply the database migrations and ensure all tables are set up:

    ```bash
    docker compose run server python manage.py migrate
    ```

    See the [Database Migrations Guide](../guide/database/migrations.md) for details.

2. **Create a Superuser Account**

    Create a technical superuser for platform administration:

    ```bash
    docker compose run server python manage.py createsuperuser --username admin
    ```

3. **Populate the Terminology Tables**

    Onconova uses an internal store of different terminology systems (e.g. SNOMED-CT, LOINC, ICD-10, etc.). To generate that store the following steps must be followed and completed.

    3.1. **Download SNOMED CT International**

    Onconova already provides most open-source terminologies in a processed form as part of its package. However, SNOMED CT International requires an additional license to use (free for academic purposes in contributing member countries). 

     - (A) Visit the [SNOMED Releases](https://mlds.ihtsdotools.org/#/viewReleases/viewRelease/167) page and login with (and create if necessary) your SNOMED credentials. 
     - (B) Locate the latest SNOMED CT International Edition release. 
     - (C) Download the `SnomedCT_InternationalRF2_PRODUCTION_***********.zip` file.

    3.2. **Import Terminologies**

    Run the following command to populate all terminology tables in the database. 

    ```bash
    docker compose run \
        -v /absolute/path/to/SnomedCT_International*.zip:/app/data/snomed.zip \
        -e ONCONOVA_SNOMED_ZIPFILE_PATH='/app/data/snomed.zip' \
        server python manage.py termsynch
    ```

    **Notes:**

    - Adjust paths and proxy details to match your environment.
    - The process may take several minutes depending on hardware and network speeds.
    - Track progress via console logs.

    !!! warning Watchout for errors

        If any errors occur during terminology synchronization, the database may remain partially populated, which can cause application errors.  
        Review logs carefully and resolve issues before using the application.

## Post-installation

After completing these steps and successfully installing Onconova you can run the following optional steps:

- **Setup Single-Sign-On through an identity provider**
    
    - You can enable signgle-sign-on through a provider (e.g. Microsoft) to facility and better controll access to Onconova.
    - Follow the instructions in the [Authentication Guide](../guide/security/authentication.md/#sso-through-identity-providers) to setup the SSO.

- **Create User Accounts and Roles**

    After creating a technical superuser you can:

    - Create additional user accounts through the client interface or server console.
    - Configure OpenID authorization with providers such as Google or Microsoft. 
    - Assign appropriate roles and access levels for clinicians, data analysts, researchers, and system administrators.

    See the [Authorization Guide](../guide/security/permissions.md) for details. 


- **Backup the Initial Database State**

    After setting up and populating terminologies:
    ```bash
    docker compose exec database pg_dump -U <db_user> <db_name> > initial_pop_backup.sql
    ```
    Store this backup in a secure location to quickly restore a clean state if needed.





