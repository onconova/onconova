from django.contrib import admin
from django.urls import path, include
from allauth.account.decorators import secure_admin_login
from pop.api import api

admin.autodiscover()
admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/", api.urls),

    path("api/accounts/", include("allauth.urls")),
    path("api/allauth/", include("allauth.headless.urls")),
]