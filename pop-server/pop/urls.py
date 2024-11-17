from django.contrib import admin
from django.urls import path
from pop.core.api import api

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/", api.urls),
]