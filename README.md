
# Installation 
1. Clone repo and navigate to the project's directory
   
2. Create or get a host SSL certificate and private key (e.g. `localhost.pem` and `localhost.key.pem` for local hosting). For local hosting you can generate the certificates using `certbot`:
    ```bash 
    sudo certbot certonly --standalone --preferred-challenges http -d localhost -d localhost
    ``` 

3. Rename `.env.sample` to `.env`. Configure the application by updating the settings in `.env`. For production, make sure to use `COMPOSE_FILE=compose.prod.yml` and to assign the paths to the host SSL certificates to the `HOST_SSL_CERTIFICATE_BUNDLE` and `HOST_SSL_CERTIFICATE_PRIVATE_KEY` variables. 

4. Run `docker compose up`,  images will be built and the containers brought up

5. On a browser, navigate to `https://${WEBAPP_HOST}:${WEBAPP_HTTPS_PORT}/` and check that the login page is rendered properly.
 


# First-time setup of the server

1. Apply migrations. Run the following command
    ```bash
    docker compose run pop-server python manage.py migrate
    ```
    to apply the database migrations and ensure all tables are created and formatted accordingly.

2. Create a superuser account. Run the command
    ```bash
    docker compose run pop-server python manage.py createsuperuser --username admin
    ```

3. Import the terminologies. 

    3.1 Download external dependencies
      - Go to `https://mlds.ihtsdotools.org/#/viewReleases/viewRelease/167` and download `SnomedCT_InternationalRF2_PRODUCTION_***********.zip`. This requires a user and license for SNOMED CT International (free for academic purposes in contributing countries).
      - Go to `https://loinc.org/download/loinc-complete/` and download `Loinc_*.**.zip`. This requires a LOINC user (free).

    3.2 Run the terminology synchronization tool
    ```bash
    docker compose run \
        -v /absolute/path/to/SnomedCT_International*.zip:/app/data/snomed.zip \
        -e SNOMED_ZIPFILE_PATH=/app/data/snomed.zip \
        -v /absolute/path/to/Loinc_*.**.zip:/app/data/loinc.zip \
        -e LOINC_ZIPFILE_PATH=/app/data/loinc.zip \
        -e LOINC_USER=loinc_username \
        -e LOINC_PASSWORD=loinc_password \
        pop-server python manage.py termsynch
    ```
