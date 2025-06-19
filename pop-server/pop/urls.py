from django.urls import path, include
from pop.api import api

urlpatterns = [
    # POP API endpoints
    path("api/v1/", api.urls),
    # Allauth API endpoints
    path("api/accounts/", include("allauth.urls")),
    path("api/allauth/", include("allauth.headless.urls")),
]
