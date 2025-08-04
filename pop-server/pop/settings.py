import os
import socket
import tomllib
from pathlib import Path

import pghistory
from corsheaders.defaults import default_headers
from pop.core.utils import mkdir_p


def secure_url(address: str):
    return f"https://{address}"


# Project base directory path
BASE_DIR = Path(__file__).resolve().parent.parent

# Read project version from pyproject.toml
with open("pyproject.toml", "rb") as f:
    VERSION = tomllib.load(f).get("tool", {}).get("poetry", {}).get("version", None)

# Django debugging mode
DEBUG = os.getenv("ENVIRONMENT") == "development"


# ----------------------------------------------------------------
# SECRETS
# ----------------------------------------------------------------

# Django secret key for cryptographic signing
SECRET_KEY = os.getenv("POP_SERVER_ENCRYPTION_KEY")
# Data anonymization secret key
ANONYMIZATION_SECRET_KEY = os.getenv("POP_SERVER_ANONYMIZATION_KEY")

# ----------------------------------------------------------------
# NETWORK
# ----------------------------------------------------------------

POP_REVERSE_PROXY_ADDRESS = (
    f'{os.getenv("POP_REVERSE_PROXY_HOST")}:{os.getenv("POP_REVERSE_PROXY_PORT")}'
)
POP_SERVER_ADDRESS = os.getenv("POP_SERVER_ADDRESS") or POP_REVERSE_PROXY_ADDRESS
POP_CLIENT_ADDRESS = os.getenv("POP_CLIENT_ADDRESS") or POP_REVERSE_PROXY_ADDRESS
POP_DOCS_ADDRESS = os.getenv("POP_DOCS_ADDRESS") or POP_REVERSE_PROXY_ADDRESS

# Controls which domains can make HTTP requests to the server.
ALLOWED_HOSTS = os.getenv("POP_SERVER_ALLOWED_HOSTS", "").split(",")
if os.getenv("ENVIRONMENT") == "development":
    ALLOWED_HOSTS.append(socket.gethostbyname(socket.gethostname()))

# URL config module
ROOT_URLCONF = "pop.urls"

# ---------------------------------------------------------------
# SECURITY
# ----------------------------------------------------------------

# Disable all CORS origins
CORS_ORIGIN_ALLOW_ALL = False
# Allowed HTTP methods for CORS
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE"]
# Allows credentials with CORS requests
CORS_ALLOW_CREDENTIALS = True
# Controls which web origins (domains) are allowed to make cross-origin AJAX requests to your Django API.
CORS_ALLOWED_ORIGINS = os.getenv("POP_SERVER_CORS_ALLOWED_ORIGINS", "").split(",") + [
    secure_url(address)
    for address in [
        POP_REVERSE_PROXY_ADDRESS,
        POP_SERVER_ADDRESS,
        POP_CLIENT_ADDRESS,
        POP_DOCS_ADDRESS,
    ]
]
# Allowed headers in CORS requests (required for authentication)
CORS_ALLOW_HEADERS = (
    *default_headers,
    "x-session-token",
    "x-email-verification-key",
    "x-password-reset-key",
)

# Cookies will only be sent over an HTTPS connection
SESSION_COOKIE_SECURE = True
# Redirect all non-HTTPS requests to HTTPS
SECURE_SSL_REDIRECT = True
# Trust the X-Forwarded-Proto header that comes from the Nginx proxy and that the request is guaranteed to be secure
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Enable HSTS for that exact domain or subdomain, and to remember it for the given number of seconds
SECURE_HSTS_SECONDS = 31536000
# Indicate that the domain owner consents to preloading
SECURE_HSTS_PRELOAD = True
# Ensure that all subdomains, not just top-level domains, can only be accessed over a secure connection
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# API pagination and throttling settings
NINJA_PAGINATION_PER_PAGE = 10
NINJA_PAGINATION_MAX_LIMIT = 50
NINJA_DEFAULT_THROTTLE_RATES = {
    "auth": "10000/day",
    "user": "10000/day",
    "anon": "1000/day",
}
NINJA_EXTRA = {"ORDERING_CLASS": "pop.core.serialization.ordering.Ordering"}


# ---------------------------------------------------------------
# INSTALLATIONS
# ----------------------------------------------------------------

# WSGI application entry point
WSGI_APPLICATION = "pop.wsgi.application"

# Installed Django + third-party + local apps
INSTALLED_APPS = [
    # Postgres triggers
    "pgtrigger",
    "pghistory",
    # POP core
    "pop.core",
    "pop.terminology",
    "pop.oncology",
    "pop.research",
    "pop.interoperability",
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
    "pop.core.history.middleware.HistoryMiddleware",
    "pop.core.history.middleware.AuditLogMiddleware",
]

# ---------------------------------------------------------------
# AUTHENTICATION
# ----------------------------------------------------------------

# Custom user model location
AUTH_USER_MODEL = "core.User"

# Authentication Enabled Backends
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Django AllAuth Configuration
SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_LOGIN_BY_CODE_ENABLED = False
ACCOUNT_EMAIL_VERIFICATION = "none"
USERSESSIONS_TRACK_ACTIVITY = True
HEADLESS_ONLY = True
HEADLESS_CLIENTS = ("app",)
HEADLESS_SERVE_SPECIFICATION = True
HEADLESS_SPECIFICATION_TEMPLATE_NAME = "headless/spec/swagger_cdn.html"

# Django AllAuth Providers
SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "APPS": [
            {
                "provider_id": "google",
                "name": "Google",
                "client_id": os.getenv("POP_GOOGLE_CLIENT_ID"),
                "secret": os.getenv("POP_GOOGLE_SECRET"),
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
                "client_id": os.getenv("POP_MICROSOFT_CLIENT_ID"),
                "secret": os.getenv("POP_MICROSOFT_SECRET"),
                "settings": {
                    "server_url": f"https://login.microsoftonline.com/{os.getenv('POP_MICROSOFT_TENANT_ID')}/v2.0",
                    "auth_params": {
                        "scope": "openid",
                        "prompt": "login",
                    },
                },
            },
        ]
    }
}

# ---------------------------------------------------------------
# DATABASE
# ----------------------------------------------------------------

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POP_POSTGRES_DATABASE"),
        "USER": os.getenv("POP_POSTGRES_USER"),
        "PASSWORD": os.getenv("POP_POSTGRES_PASSWORD"),
        "HOST": os.getenv("POP_POSTGRES_HOST"),
        "PORT": os.getenv("POP_POSTGRES_PORT"),
    },
}

# Postgres trigger-based event tracking configuration
PGHISTORY_CONTEXT_FIELD = pghistory.ContextJSONField()
PGHISTORY_FIELD = pghistory.Field(null=True)
PGHISTORY_OBJ_FIELD = pghistory.ObjForeignKey(db_index=True)
PGHISTORY_DEFAULT_TRACKERS = (
    pghistory.InsertEvent(label="create"),
    pghistory.UpdateEvent(label="update"),
    pghistory.DeleteEvent(label="delete"),
    pghistory.ManualEvent(label="import"),
    pghistory.ManualEvent(label="export"),
)

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


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
mkdir_p("/app/logs")
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
