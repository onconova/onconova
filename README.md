<a name="readme-top"></a>

<!-- PROJECT LOGO -->

<br />
<div align="center">
    <a href="https://github.com/luisfabib/pop">
        <img src="pop-client/src/assets/images/logo.svg" width="10%">
    </a>
    <h1 style="border-bottom: none;">Precision Oncology Platform</h1>

[![releases](https://img.shields.io/github/v/release/luisfabib/pop)](https://github.com/luisfabib/pop)
[![license](https://img.shields.io/github/license/luisfabib/pop.svg)](https://github.com/luisfabib/pop/blob/main/LICENSE)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/luisfabib/pop)

  <p align="center">
    The Precision Oncology Platform (POP) is an open-source project aimed at capturing and structuring clinical data from oncology patients, while enabling interactive aggregated data analysis.
    <br />
    <br />
    <a href="https://luisfabib.github.io/pop "><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/luisfabib/pop/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/luisfabib/pop/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

# Installation 

Follow these steps to install and set up the Precision Oncology Platform (POP) on a Linux-based machine:

1. **Clone the repository** - Download the code repository navigate to the project's directory
    ```bash
    git clone https://github.com/luisfabib/pop.git
    cd pop
    ```
   
2. **Setup Host SSL Certificates** - Create or get a host SSL certificate and private key (e.g. `localhost.pem` and `localhost.key.pem` for local hosting). 

    *Tip:* For local hosting you can generate the certificates using `certbot`:
    ```bash 
    sudo certbot certonly --standalone --preferred-challenges http -d localhost -d localhost
    ``` 
    

3. **Configure the environment** - Setup the environment variables to configure the installation to your machine and its network.

    - Copy the contents of `.env.sample` to new `.env` file.
    ```bash
    cp .env.sample .env
    ```

    - Update the .env file with your configuration settings:
        - Provide the paths to the host SSL certificates in `HOST_SSL_CERTIFICATE_BUNDLE` and `HOST_SSL_CERTIFICATE_PRIVATE_KEY`.

        - Set `COMPOSE_FILE=compose.prod.yml` for production environments.

4. **Build and Run the Containers** - The following command will build the images and start the containers containing the application:
    ```bash
    docker compose up
    ```

5. **Access the Web App** - Navigate to `https://${WEBAPP_HOST}:${WEBAPP_HTTPS_PORT}/` in your browser to ensure the login page is rendered correctly.
 
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## First-time setup of the server

1. **Apply migrations** - Run the following command to apply the database migrations and ensure all tables are set up:
    ```bash
    docker compose run pop-server python manage.py migrate
    ```

2. **Create a Superuser Account** - Create a superuser to start administrating the server and client applications:
    ```bash
    docker compose run pop-server python manage.py createsuperuser --username admin
    ```

3. **Import the terminologies**. 
    
    POP uses an internal store of different terminology systems (e.g. SNOMED-CT, LOINC, ICD-10, etc.). To generate that store several external terminology artifacts must be downloaded and imported into the database. Follow these steps to achieve that:

    3.1 **Download external dependencies** - Most terminologies will be automatically downloaded and handled by the software, however both SNOMED-CT and LOINC require login credentials and license agreements that have to be accepted first: 
      - Go to `https://mlds.ihtsdotools.org/#/viewReleases/viewRelease/167` and download `SnomedCT_InternationalRF2_PRODUCTION_***********.zip`. This requires a user and license for SNOMED CT International (free for academic purposes in contributing countries).
      - Go to `https://loinc.org/download/loinc-complete/` and download `Loinc_*.**.zip`. This requires a LOINC user (free).

    3.2 **Generate the terminology store** - Once you’ve downloaded the terminology files, run the following command to synchronize them:
    ```bash
    docker compose run \
        -v /absolute/path/to/SnomedCT_International*.zip:/app/data/snomed.zip \
        -e SNOMED_ZIPFILE_PATH='/app/data/snomed.zip' \
        -v /absolute/path/to/Loinc_*.**.zip:/app/data/loinc.zip \
        -e LOINC_ZIPFILE_PATH='/app/data/loinc.zip' \
        pop-server python manage.py termsynch
    ```

    *Note:* If your machine is behind a corporate proxy and/or with root CA certificates add the following arguments to the command:
    ```bash
    # Copy certificates
    cp <local/path/to/root_ca_certificates.pem> ./pop-server/etc/certs/root_ca_certificates.pem
    # Create store with proxy settings setup
    docker compose run \
        ...
        -e http_proxy='http://<username>:<password>@<hostname>:<port>' \
        -e https_proxy='http://<username>:<password>@<hostname>:<port>' \
        -e ROOT_CA_CERTIFICATES='./etc/certs/root_ca_certificates.pem' \
        pop-server python manage.py termsynch
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Building images behind a corporate proxy and with root CA certificates

To ensure that the images are built properly

1. Copy root CA certificate to server build context
    ```bash
    cp <local/path/to/root_ca_certificates.pem> ./pop-server/etc/certs/root_ca_certificates.pem
    ```

2. Build all images through proxy and with trusted root CA certificates
    ```bash
    docker compose build \
        --build-arg http_proxy='http://<username>:<password>@<hostname>:<port>' \
        --build-arg https_proxy='http://<username>:<password>@<hostname>:<port>' \
        --build-arg ROOT_CA_CERTIFICATES='./etc/certs/root_ca_certificates.pem'
    ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazing_feature`)
3. Commit your Changes (`git commit -m 'Add some amazing feature'`)
4. Push to the Branch (`git push origin feature/amazing_feature`)
5. Open a Pull Request (PR)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See ![LICENSE](https://github.com/luisfabib/pop?tab=MIT-1-ov-file) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>