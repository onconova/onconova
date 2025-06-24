import os
import tomllib
import pghistory
import socket
from pathlib import Path
from corsheaders.defaults import default_headers

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
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
# Data anonymization secret key
ANONYMIZATION_SECRET_KEY = os.getenv("ANONYMIZATION_SECRET_KEY")

# ----------------------------------------------------------------
# NETWORK
# ----------------------------------------------------------------

# Hosts the app is allowed to serve
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS").split(",")
if os.getenv("ENVIRONMENT") == "development":
    ALLOWED_HOSTS = ALLOWED_HOSTS + [socket.gethostbyname(socket.gethostname())]
# Port the app is allowed to serve
HOST_PORT = os.getenv("WEBAPP_HTTPS_PORT")
# Host of the client application
WEBAPP_HOST = os.getenv("WEBAPP_HOST")
# Name of the providing organization (internal use)
HOST_ORGANIZATION = os.getenv("ORGANIZATION_NAME")
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
# Explicitly allowed CORS origins
CORS_ALLOWED_ORIGINS = [f"https://{WEBAPP_HOST}"]
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
    "pop.core.history.middleware.APILoggingMiddleware",
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
        "NAME": os.getenv("POSTGRES_DATABASE"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    },
}

# Postgres trigger-based event tracking configuration
PGHISTORY_CONTEXT_FIELD = pghistory.ContextJSONField()
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

# Logger settings
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(levelname)s %(asctime)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filters": [],
            "filename": "/app/logs/logfile.log",
            "when": "midnight",
            "backupCount": 31,
            "formatter": "simple",
        },
    },
    "loggers": {
        "api": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
