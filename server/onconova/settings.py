"""
Django settings module for the Onconova server application.

This module configures environment variables, security, authentication, database, logging, and other core settings for the Onconova Django project.
"""
import os
import socket
import tomllib  # type: ignore
from pathlib import Path

import pghistory
from corsheaders.defaults import default_headers

from onconova.core.utils import mkdir_p


def secure_url(address: str):
    return f"https://{address}"


BASE_DIR = Path(__file__).resolve().parent.parent
"""
Project base directory path
"""

if BASE_DIR.joinpath("pyproject.toml").exists():
    # Read project version from pyproject.toml
    with open(BASE_DIR / "pyproject.toml", "rb") as f:
        VERSION = tomllib.load(f).get("tool", {}).get("poetry", {}).get("version", None)
        """
    Version of the Onconova project, set automatically based on package version.
    """
else:
    VERSION = "unknown"

DEBUG = os.getenv("ENVIRONMENT") == "development"
"""
Flag indicating whether the application is in development mode
"""

# ----------------------------------------------------------------
# SECRETS
# ----------------------------------------------------------------

SECRET_KEY = os.getenv("ONCONOVA_SERVER_ENCRYPTION_KEY")
"""
Django secret key for cryptographic signing
"""

ANONYMIZATION_SECRET_KEY = os.getenv("ONCONOVA_SERVER_ANONYMIZATION_KEY")
"""
Data anonymization secret key
"""

# ----------------------------------------------------------------
# NETWORK
# ----------------------------------------------------------------

ONCONOVA_REVERSE_PROXY_ADDRESS = f'{os.getenv("ONCONOVA_REVERSE_PROXY_HOST")}:{os.getenv("ONCONOVA_REVERSE_PROXY_PORT")}'
"""
Reverse proxy address for the Onconova server
"""

ONCONOVA_SERVER_ADDRESS = (
    os.getenv("ONCONOVA_SERVER_ADDRESS") or ONCONOVA_REVERSE_PROXY_ADDRESS
)
"""
Onconova server address
"""

ONCONOVA_CLIENT_ADDRESS = (
    os.getenv("ONCONOVA_CLIENT_ADDRESS") or ONCONOVA_REVERSE_PROXY_ADDRESS
)
"""
Onconova client address
"""

ALLOWED_HOSTS = os.getenv("ONCONOVA_SERVER_ALLOWED_HOSTS", "").split(",")
"""
List of allowed hosts for the Onconova server
"""
if os.getenv("ENVIRONMENT") == "development":
    ALLOWED_HOSTS.append(socket.gethostbyname(socket.gethostname()))

ROOT_URLCONF = "onconova.urls"
"""
Module path for the URL configuration
"""

# ---------------------------------------------------------------
# SECURITY
# ----------------------------------------------------------------

CORS_ORIGIN_ALLOW_ALL = False
"""
Flag indicating that all origins are not allowed for CORS requests
"""

CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE"]
"""
List of allowed HTTP methods for CORS requests
"""

CORS_ALLOW_CREDENTIALS = True
"""
Flag indicating that credentials are allowed with CORS requests
"""

CORS_ALLOWED_ORIGINS = os.getenv("ONCONOVA_SERVER_CORS_ALLOWED_ORIGINS", "").split(
    ","
) + [
    secure_url(address)
    for address in [
        ONCONOVA_REVERSE_PROXY_ADDRESS,
        ONCONOVA_SERVER_ADDRESS,
        ONCONOVA_CLIENT_ADDRESS,
    ]
]
"""
Controls which web origins (domains) are allowed to make cross-origin AJAX requests to your Django API.
"""

CORS_ALLOW_HEADERS = (
    *default_headers,
    "x-session-token",
    "x-email-verification-key",
    "x-password-reset-key",
)
"""
List of allowed headers in CORS requests (required for authentication)
"""

SESSION_COOKIE_SECURE = True
"""
Flag indicating that cookies will only be sent over an HTTPS connection
"""

SECURE_SSL_REDIRECT = True
"""
Flag indicating that all non-HTTPS requests should be redirected to HTTPS
"""

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
"""
Trust the `X-Forwarded-Proto` header that comes from the Nginx reverse-proxy and that the request is guaranteed to be secure
"""

SECURE_HSTS_SECONDS = 31536000
"""
Enable HSTS for that exact domain or subdomain, and to remember it for the given number of seconds
"""

SECURE_HSTS_PRELOAD = True
"""
Indicates that the domain owner consents to preloading
"""

SECURE_HSTS_INCLUDE_SUBDOMAINS = True
"""
Ensures that all subdomains, not just top-level domains, can only be accessed over a secure connection
"""

# API pagination and throttling settings
NINJA_PAGINATION_PER_PAGE = 10
"""
Sets the default number of items per page for pagination in the Django-Ninja API framework
"""

NINJA_PAGINATION_MAX_LIMIT = 50
"""
Sets the maximal number of items per page for pagination in the Django-Ninja API framework
"""

NINJA_DEFAULT_THROTTLE_RATES = {
    "auth": "10000/day",
    "user": "10000/day",
    "anon": "1000/day",
}
"""
Default throttle rates for the Django-Ninja API framework
"""

NINJA_EXTRA = {"ORDERING_CLASS": "onconova.core.serialization.ordering.Ordering"}
"""
Adds a custom ordering class for the Django-Ninja API framework
"""

# ---------------------------------------------------------------
# INSTALLATIONS
# ----------------------------------------------------------------

WSGI_APPLICATION = "onconova.wsgi.application"
"""
Use the WSGI application as entry-point 
"""

INSTALLED_APPS = [
    # Postgres triggers
    "pgtrigger",
    "pghistory",
    # Onconova core
    "onconova.core",
    "onconova.terminology",
    "onconova.oncology",
    "onconova.research",
    "onconova.interoperability",
    # Django AllAuth
    "allauth",
    "allauth.account",
    "allauth.headless",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.openid_connect",
    "allauth.usersessions",
    # Django Extensions
    "ninja_extra",
    "corsheaders",
    "django_extensions",
    # Django Core
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
"""
List of installed Django, 3rd-party, and local apps
"""

# Middleware stack
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.usersessions.middleware.UserSessionsMiddleware",
    "onconova.core.history.middleware.HistoryMiddleware",
    "onconova.core.history.middleware.AuditLogMiddleware",
]
"""
List of installed middlewares.
"""


# ---------------------------------------------------------------
# AUTHENTICATION
# ----------------------------------------------------------------

AUTH_USER_MODEL = "core.User"
"""
Assign the Onconova `User` as default user model
"""

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
]
"""
List of installed authentication backends
"""

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
"""
List password validators
"""

# Django AllAuth Configuration
SITE_ID = 1

ACCOUNT_LOGIN_METHODS = {"email", "username"}
"""
Allow both login by using the email or username as identifier.
"""

ACCOUNT_LOGIN_BY_CODE_ENABLED = False
"""
Do not allow login by code using Allauth
"""

ACCOUNT_EMAIL_VERIFICATION = "none"
"""
Disable Allauth's email verification
"""

USERSESSIONS_TRACK_ACTIVITY = True
"""
Track user sessions for audit trail purposes
"""

HEADLESS_ONLY = True
"""
Only enable the Allauth headless API mode
"""

HEADLESS_CLIENTS = ("app",)
"""
Only allow Allauth's headless `app`-mode.
"""

HEADLESS_SERVE_SPECIFICATION = True
"""
Provide an URL endpoint to serve the internal Allauth OpenAPI specification
"""

HEADLESS_SPECIFICATION_TEMPLATE_NAME = "headless/spec/swagger_cdn.html"
"""
Configuration for Django AllAuth social authentication providers
"""

SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "APPS": [
            {
                "provider_id": "google",
                "name": "Google",
                "client_id": os.getenv("ONCONOVA_GOOGLE_CLIENT_ID"),
                "secret": os.getenv("ONCONOVA_GOOGLE_SECRET"),
                "settings": {
                    "server_url": "https://accounts.google.com",
                    "auth_params": {
                        "scope": "openid email profile",
                        "prompt": "login",
                    },
                },
            },
            {
                "provider_id": "microsoft",
                "name": "Microsoft",
                "client_id": os.getenv("ONCONOVA_MICROSOFT_CLIENT_ID"),
                "secret": os.getenv("ONCONOVA_MICROSOFT_SECRET"),
                "settings": {
                    "server_url": f"https://login.microsoftonline.com/{os.getenv('ONCONOVA_MICROSOFT_TENANT_ID')}/v2.0",
                    "auth_params": {
                        "scope": "openid",
                        "prompt": "login",
                    },
                },
            },
        ]
    }
}
"""
Configuration for Django AllAuth social authentication providers
"""

# ---------------------------------------------------------------
# DATABASE
# ----------------------------------------------------------------

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("ONCONOVA_POSTGRES_DATABASE"),
        "USER": os.getenv("ONCONOVA_POSTGRES_USER"),
        "PASSWORD": os.getenv("ONCONOVA_POSTGRES_PASSWORD"),
        "HOST": os.getenv("ONCONOVA_POSTGRES_HOST"),
        "PORT": os.getenv("ONCONOVA_POSTGRES_PORT"),
    },
}
"""
Onconova database connection configuration
"""

# Postgres trigger-based event tracking configuration
PGHISTORY_CONTEXT_FIELD = pghistory.ContextJSONField()
"""
Context information for the trigger-based history tracking
"""

PGHISTORY_FIELD = pghistory.Field(null=True)
"""
Make history model fields nullable by default
"""

PGHISTORY_OBJ_FIELD = pghistory.ObjForeignKey(db_index=True)
"""
Make pghistory foreign key fields indexed by default
"""

PGHISTORY_DEFAULT_TRACKERS = (
    pghistory.InsertEvent(label="create"),
    pghistory.UpdateEvent(label="update"),
    pghistory.DeleteEvent(label="delete"),
    pghistory.ManualEvent(label="import"),
    pghistory.ManualEvent(label="export"),
)
"""
List of default pghistory event trackers
"""

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
"""
Use integers as primary keys for history model tables
"""

# ---------------------------------------------------------------
# TEMPLATES
# ----------------------------------------------------------------

# Django template settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]
# URL to use when referring to static files located in STATIC_ROOT
STATIC_URL = "/static/"
# Absolute path to the directory where collectstatic will collect static files for deployment
STATIC_ROOT = "/app/static"
# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = "/app/media"
# URL that handles the media served from MEDIA_ROOT, used for managing stored files
MEDIA_URL = "/media/"

# ---------------------------------------------------------------
# INTERNATIONALIZATION
# ----------------------------------------------------------------

# Internationalization
LANGUAGE_CODE = "en-us"  # US English
TIME_ZONE = "Europe/Berlin"  # Central European time
USE_I18N = True  # Enable Django’s translation system
USE_TZ = False  # Do not make datetimes timezone-aware by default

# ---------------------------------------------------------------
# LOGGING
# ----------------------------------------------------------------

# Ensure logs directory exists
try:
    mkdir_p("/app/logs")
except PermissionError: pass
# Logger settings
LOGGING = {
    "version": 1,
    "disable_existing_loggers": not DEBUG,
    "formatters": {
        "audit_logfmt": {
            "format": (
                'timestamp="%(asctime)s" level=%(levelname)s user.username="%(username)s" user.id="%(user_id)s" user.level=%(access_level)s '
                'request.ip="%(ip)s" request.agent="%(user_agent)s" request.method=%(method)s request.path="%(path)s" '
                "response.status=%(status_code)s response.duration=%(duration)s "
                'request.data="%(request_data)s" response.data="%(response_data)s"'
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S%z",
        },
        "error_verbose": {
            "format": (
                "[%(asctime)s] %(levelname)s in %(module)s: %(message)s\n"
                "%(exc_info)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "audit_file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "filename": "/app/logs/logfile.log",
            "formatter": "audit_logfmt",
            "backupCount": 31,
        },
        "audit_console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "audit_logfmt",
        },
        "error_console": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "formatter": "error_verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "filename": "/app/logs/error.log",
            "formatter": "error_verbose",
            "backupCount": 31,
        },
    },
    "loggers": {
        "audit": {
            "handlers": ["audit_file", "audit_console"],
            "level": "INFO",
            "propagate": False,
        },
        "error": {
            "handlers": ["error_file", "error_console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
