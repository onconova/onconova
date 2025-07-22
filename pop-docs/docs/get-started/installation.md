

The following sections will guide you through the installation and initial configuration of the Precision Oncology Platform (POP) on a Linux-based machine. 
Make sure that your hardware and network fulfill the [minimal requirements](requirements.md) for installing POP.

!!! info "Internet Access"

    The installation and setup of POP is the only instance where **an open connection to the Internet** will be required. 
    This is necessary to download the different POP components, third-party packages, and other relevant files required for its function.

    For security reasons, **your network may require a proxy configuration and/or root CA certificates to connect to the internet**. 
    If a command requires an active internet connection, you can switch to a tab where the same command with the added configuration for your network will be shown.


### Install From Source

Follow these steps to install and set up POP from its source code.

1. **Clone the Repository**

    Download the POP source code and navigate to the project directory:
    ```bash
    git clone https://github.com/luisfabib/pop.git
    cd pop
    ```
   
2. **Setup Host SSL Certificates**

    SSL certificates (, i.e `.pem` files) are required to serve the application securely.
        
    === "Local hosting"

        To generate self-signed certificates for local hosting, you can use certbot:
        ```bash 
        sudo certbot certonly --standalone --preferred-challenges http -d localhost -d localhost
        ``` 

        This will generate your certificates, typically at:

        ```
        /etc/letsencrypt/live/localhost/fullchain.pem
        /etc/letsencrypt/live/localhost/privkey.pem
        ```

        Adjust the paths in your `.env` accordingly (see below).

    === "Hosting Within an Organization"

        If hosting within a corporate network, contact your IT department to request SSL certificates for the domain where the POP instance will be hosted.
        
        Copy the certificates into a local folder and adjust the paths in your `.env` accordingly (see below).

3. **Configure the environment**

    Set up the environment variables to configure the installation for your machine and network:

    - Copy the provided `.env.sample` to `.env`.
        ```bash
        cp .env.sample .env
        ```

    - Update the `.env` file with your configuration settings:
        - Set the absolute paths to your SSL certificates:
            ```bash
            POP_REVERSE_PROXY_SSL_CERTIFICATE_BUNDLE='/path/to/fullchain.pem'
            POP_REVERSE_PROXY_SSL_CERTIFICATE_PRIVATE_KEY='/path/to/privkey.pem'
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

        - Set all other non-optional environment variables listed in the [Configuration section](configuration.md#pop-environment-variables-reference) based on your environment.

4. **Build and Run the Containers**

    Build and start the POP containers:

    === "Normal"

        ```bash
        docker compose up --build -d
        ```

    === "With proxy and/or root certificates"

        1. Copy the root CA certificates
            ```bash 
            cp <local-path/root-ca-certificates.pem> ./pop-server/etc/certs/root-ca-certificates.pem
            cp <local-path/root-ca-certificates.pem> ./pop-client/etc/certs/root-ca-certificates.pem
            cp <local-path/root-ca-certificates.pem> ./pop-docs/etc/certs/root-ca-certificates.pem
            ```

        2. Build the POP images:

            ```bash
            docker compose build \
                --build-arg http_proxy='http://<username>:<password>@<hostname>:<port>' \
                --build-arg https_proxy='http://<username>:<password>@<hostname>:<port>' \
                --build-arg ROOT_CA_CERTIFICATES='./etc/certs/root-ca-certificates.pem'
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
    ************   nginx:1.23           "/docker-entrypoint.…"   pop-nginx
    ************   pop-client           "docker-entrypoint.s…"   pop-client
    ************   pop-server           "python manage.py ru…"   pop-server
    ************   pop-docs             "mkdocs serve -a 0.0…"   pop-docs
    ************   postgres:13-alpine   "docker-entrypoint.s…"   pop-postgres
    ```



5. **Access the Web Application**

    Open your browser and visit:
    ```
    https://${POP_REVERSE_PROXY_HOST}:${POP_REVERSE_PROXY_HTTPS_PORT}/
    ```
    Verify that the login page loads correctly. If so, the POP components have been successfully installed. 

    If this is a fresh install of POP, please proceed to the next section and complete its steps before using the platform any further.


## First-time Setup of the Database

Before using POP, the database must be configured and populated with required clinical terminology data.

!!! note "First-time only"

    If you already have a configured and populated POP database, you can skip these steps. 

1. **Apply migrations**

    Run the following command to apply the database migrations and ensure all tables are set up:

    ```bash
    docker compose run pop-server python manage.py migrate
    ```

    See the [Database Migrations Guide](../guide/database/migrations.md) for details.

2. **Create a Superuser Account**

    Create a technical superuser for platform administration:

    ```bash
    docker compose run pop-server python manage.py createsuperuser --username admin
    ```

3. **Populate the Terminology Tables**

    POP uses an internal store of different terminology systems (e.g. SNOMED-CT, LOINC, ICD-10, etc.). To generate that store several external terminology artifacts must be downloaded and imported into the database. POP provides automated services that will take care of locating, downloading, and processing the different terminology artifacts. Follow these steps to achieve this.

    1. **Download external dependencies**

        Most terminologies will be automatically downloaded and handled by the software, however access to both SNOMED-CT and LOINC require login credentials and license agreements that have to be accepted first: 

        - *SNOMED CT*
            - (A) Visit the [SNOMED Releases](https://mlds.ihtsdotools.org/#/viewReleases/viewRelease) page and login with (and create if necessary) your SNOMED credentials. This requires a license for SNOMED CT International (free for academic purposes in contributing countries).
            - (B) Locate the latest SNOMED CT International Edition release. 
            - (C) Download the `SnomedCT_InternationalRF2_PRODUCTION_***********.zip` file. This requires a user and license for SNOMED CT International (free for academic purposes in contributing countries).

        - *LOINC*
            - (A) Go to the [LOINC File Access](https://loinc.org/download/loinc-complete) page and login with (and create if necessary) your LOINC credentials. 
            - (B) Download the latest `Loinc_*.**.zip` file.

    2. **Run the automatization pipeline**

        Once you’ve downloaded the terminology files, run the following command to populate all terminology tables in the database. 

        === "Normal"

            ```bash
            docker compose run \
                -v /absolute/path/to/SnomedCT_International*.zip:/app/data/snomed.zip \
                -e POP_SNOMED_ZIPFILE_PATH='/app/data/snomed.zip' \
                -v /absolute/path/to/Loinc_*.**.zip:/app/data/loinc.zip \
                -e POP_LOINC_ZIPFILE_PATH='/app/data/loinc.zip' \
                pop-server python manage.py termsynch
            ```

        === "With proxy and/or root certificates"

            ```bash
            docker compose run \
                -v /absolute/path/to/SnomedCT_International*.zip:/app/data/snomed.zip \
                -e POP_SNOMED_ZIPFILE_PATH='/app/data/snomed.zip' \
                -v /absolute/path/to/Loinc_*.**.zip:/app/data/loinc.zip \
                -e POP_LOINC_ZIPFILE_PATH='/app/data/loinc.zip' 
                -e http_proxy='http://<username>:<password>@<hostname>:<port>' \
                -e https_proxy='http://<username>:<password>@<hostname>:<port>' \
                -e ROOT_CA_CERTIFICATES='./etc/certs/root-ca-certificates.pem' \
                pop-server python manage.py termsynch
            ```

        **Notes:**

        - Adjust paths and proxy details to match your environment.
        - The process may take several minutes depending on file sizes and network speed.
        - Track progress via console logs.


        !!! warning Watchout for errors

            If any errors occur during terminology synchronization, the database may remain partially populated, which can cause application errors.  
            Review logs carefully and resolve issues before using the application.

## Post-installation

After completing these steps and successfully installing POP you can run the following optional steps:

- **Setup Single-Sign-On through an identity provider**
    
    - You can enable signgle-sign-on through a provider (e.g. Microsoft) to facility and better controll access to POP.
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
    docker compose exec pop-db pg_dump -U <db_user> <db_name> > initial_pop_backup.sql
    ```
    Store this backup in a secure location to quickly restore a clean state if needed.





