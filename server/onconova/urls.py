from django.urls import include, path

from onconova.api import api

urlpatterns = [
    # ONCONOVA API endpoints
    path("api/v1/", api.urls),
    # Allauth API endpoints
    path("api/accounts/", include("allauth.urls")),
    path("api/allauth/", include("allauth.headless.urls")),
]
