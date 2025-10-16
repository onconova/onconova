"""
This module defines the URL routing configuration for the Onconova Django application.
It includes API endpoints for the Onconova API, as well as authentication endpoints
provided by Django Allauth and Allauth Headless.
"""

from django.urls import URLPattern, include, path

from onconova.api import api

urlpatterns: list[URLPattern]
"""URL Patterns resolved by Django:

- `api/v1/`: Routes to Onconova API v1 endpoints.
- `api/accounts/`: Includes internal Django Allauth authentication endpoints.
- `api/allauth/`: Includes internal Allauth Headless authentication endpoints.
"""
urlpatterns = [
    # Onconova API endpoints
    path("api/v1/", api.urls),
    # Allauth API endpoints
    path("api/accounts/", include("allauth.urls")),
    path("api/allauth/", include("allauth.headless.urls")),
]
