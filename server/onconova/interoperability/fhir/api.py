"""
This module defines and configures the main Onconova API using NinjaExtraAPI, providing a secure, 
standards-based interface for cancer genomics and clinical research data management. It registers all core, 
oncology, research, and interoperability controllers, and sets up OpenAPI documentation with custom settings and license information.
"""

from ninja import Redoc
from ninja_extra import NinjaExtraAPI

from onconova.interoperability.fhir.controllers import (
    PatientController
)

api:NinjaExtraAPI 
"""An Onconova FHIR API, This API serves as the entry point for all FHIR RESTful endpoints"""

api = NinjaExtraAPI(
    title="Onconova FHIR API",
    urls_namespace="onconova.fhir",
    servers=[
        dict(
            url="https://{domain}:{port}/api/fhir",
            description="FHIR API server",
            variables={"port": {"default": "4443"}, "domain": {"default": "localhost"}},
        ),
    ],
    openapi_extra=dict(
        info=dict(
            license=dict(
                name="MIT",
                url="https://github.com/luisfabib/onconova/blob/main/LICENSE",
            )
        )
    ),
    docs_url=None,
)
api.description = """
Welcome to the Onconova FHIR API — a secure, FHIR-based interface designed to facilitate the exchange, management, and 
analysis of research data related to cancer genomics, clinical records, and associated metadata. 
This API implements the FHIR operations defined in the Onconova FHIR Implementation Guide [CapabilityStatement](https://luisfabib.github.io/onconova/dev/fhir-ig/CapabilityStatement-onconova-capability-statement.html).

### Authentication
To ensure the security and integrity of cancer research data, **all API requests require proper authentication**.

A valid session token must be obtained prior to accessing any protected endpoint. This token must be included in the request header `X-Session-Token`.

The authentication and authorization flows for obtaining and managing session tokens are provided through the AllAuth authentication service. 
This includes endpoints for user login, logout, password management, and token renewal. For complete details on implementing authentication and 
managing session tokens, please refer to the [AllAuth API documentation](https://docs.allauth.org/en/latest/headless/openapi-specification/).

**Important:** Unauthorized requests or those missing valid authentication tokens will receive an `HTTP 401 Unauthorized` response.

### Terms and Conditions
By accessing and using this website, you agree to comply with and be bound by the following terms and conditions. The content provided on this API is 
intended solely for general informational and research purposes. While we strive to ensure the information is accurate and reliable, we do not make 
any express or implied warranties about the accuracy, adequacy, validity, reliability, availability, or completeness of the content.

The information presented on this platform is provided in good faith. However, we do not accept any liability for any loss or damage incurred as a 
result of using the site or relying on the information provided. Your use of this site and any reliance on the content is solely at your own risk.

These terms and conditions may be updated from time to time, and it is your responsibility to review them regularly to ensure compliance.

### License 
The Onconova FHIR API specification is made available under the MIT License, a permissive open-source license that allows users to freely use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the inclusion of the original copyright and license.
    """
api.register_controllers(
    PatientController,
)
