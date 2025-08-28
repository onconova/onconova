<br />
<div align="center">
    <a href="https://github.com/luisfabib/onconova">
        <img src="onconova-client/src/assets/images/logo.svg" width="10%">
    </a>
    <h1 style="border-bottom: none;">Precision Oncology Platform</h1>

[![releases](https://img.shields.io/github/v/release/luisfabib/onconova)](https://github.com/luisfabib/onconova)
[![license](https://img.shields.io/github/license/luisfabib/onconova.svg)](https://github.com/luisfabib/onconova/blob/main/LICENSE)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/luisfabib/onconova)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Angular](https://img.shields.io/badge/angular-%23DD0031.svg?style=for-the-badge&logo=angular&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)


  <p align="center">
    The Precision Oncology Platform (Onconova) is an open-source project aimed at capturing and structuring cancer-related clinical data, while enabling interactive aggregated data analysis.
    <br />
    <br />
    <a href="https://luisfabib.github.io/onconova "><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/luisfabib/onconova/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/luisfabib/onconova/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>


## Features

 **🖥️ API Server**  
    Robust CRUD API for clinical resources, designed with the OpenAPI 3.1 standard for seamless data manipulation and exchange.

**🌐 Web Client**  
    Modern Angular-based interface for intuitive interaction with clinical data and API endpoints.

**📋 Structured Data Collection**  
    Streamlined capture of research data in standardized formats, securely stored in a relational PostgreSQL database.

**📊 Interactive Data Exploration**  
    Powerful cohort creation, real-time filtering, and visualization tools for dynamic data analysis.

**🔒 Data Protection**  
    Automated anonymization features to help ensure compliance with data privacy regulations.

**🚀 Effortless Deployment**  
    Fully Dockerized architecture for quick setup and reliable production deployment.

**🧩 Extensible & Customizable**  
    Plugin system enables institution-specific enhancements without altering the core platform.

## Installation

Checkout the [Installation Guide](https://luisfabib.github.io/onconova/get-started/installation/) for detailed setup instructions.

If you need help, consult the [FAQ](https://luisfabib.github.io/onconova/get-started/faq/) or [open an issue](https://github.com/luisfabib/onconova/issues).

### Prerequisites

See the [requirements](https://luisfabib.github.io/onconova/get-started/requirements/) for supported platforms and dependencies.


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

### Development Setup

Follow the [Installation Guide](../../get-started/installation.md) to set up Onconova for local development using Docker Compose.

Use the `compose.dev.yml` file for development. You can specify it directly when starting the containers:
```sh
docker compose -f compose.dev.yml up --build -d
```
or set the environment variable:
```sh
export COMPOSE_FILE=compose.dev.yml
```

The development containers are configured to mount your local source code into the container. Any changes you make to your code are immediately reflected inside the container, automatically restarting the server or client as needed. This enables live development without requiring you to install all dependencies on your local machine.

### Testing

Onconova includes a comprehensive test suite to ensure all components function as intended. The testing strategy varies depending on whether you are working on the server, the client, or both.

Run server-side unit tests using [Pytest](https://docs.pytest.org/en/stable/) within the Docker container:
```sh
docker compose run --rm server pytest -W ignore
```
These tests cover backend models, API endpoints, and core logic. Before submitting changes, verify that all tests pass and consider adding new tests for any new features or bug fixes.

Execute client-side Angular unit tests:
```sh
docker compose run --rm client npm run test:ci
```
Automated tests validate UI components, services, and client logic. In addition to running these tests, manually test the application (especially any new or modified components) on your development instance to confirm expected behavior and usability.

<!-- LICENSE -->
## License

Distributed under the MIT License. See [LICENSE](https://github.com/luisfabib/onconova?tab=MIT-1-ov-file) for more information.
