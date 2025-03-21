"""
Django settings for pop-server.
"""

from pathlib import Path
import os 
import environ
import tomllib
import socket
import datetime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'), overwrite=True)

# parse and set the project version
with open("pyproject.toml", "rb") as f:
    VERSION = tomllib.load(f).get('tool',{}).get('poetry',{}).get('version', None)

# Security configuration
SECRET_KEY = env("DJANGO_SECRET_KEY")  
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS").split(",") + ['testserver']
ALLOWED_HOSTS += [socket.gethostbyname(socket.gethostname())]
WEBAPP_HOST = env('WEBAPP_HOST')
HOST_PORT = env('WEBAPP_HTTPS_PORT')
HOST_ORGANIZATION = env('ORGANIZATION_NAME') # Used by API

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'DELETE']

# Django debugging mode
DEBUG = env("DEBUG")                         # A boolean that turns on/off debug mode (never deploy a site into production with DEBUG turned on)

# HTTPS Settings
SESSION_COOKIE_SECURE = True                # Cookie will only be sent over an HTTPS connection
SECURE_SSL_REDIRECT = True                  # Redirect all non-HTTPS requests to HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")   # Trust the X-Forwarded-Proto header that comes from the Nginx proxy and that the request is guaranteed to be secure

# HTTP Strict Transport Security (HSTS) settings
SECURE_HSTS_SECONDS = 31536000              # Enable HSTS for that exact domain or subdomain, and to remember it for the given number of seconds
SECURE_HSTS_PRELOAD = True                  # Indicate that the domain owner consents to preloading (may eventually become unnecessary)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True       # Ensure that all subdomains, not just top-level domains, can only be accessed over a secure connection

# Application definition
INSTALLED_APPS = [
    'django_extensions',
    'pop.core',
    'pop.terminology',
    'pop.oncology',
    'pop.interoperability',
    'pop.analytics',
    'ninja_extra',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Register the custom user (do not change)
AUTH_USER_MODEL = 'core.User'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',            # Provide several security enhancements to the request/response cycle
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',     # Enable session functionality
    # 'django.middleware.csrf.CsrfViewMiddleware',                # Add protection against Cross Site Request Forgeries by adding hidden form fields to POST forms and checking requests for the correct value
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Add the user attribute, representing the currently-logged-in user, to every incoming HttpRequest object
    'django.contrib.messages.middleware.MessageMiddleware',     # Enable cookie- and session-based message support
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # Add simple clickjacking protection via the X-Frame-Options header 
]

NINJA_JWT = {
    "AUTH_TOKEN_CLASSES": ("ninja_jwt.tokens.AccessToken","ninja_jwt.tokens.RefreshToken"),
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=env("ACCESS_TOKEN_LIFETIME", default=30)),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=env("REFRESH_TOKEN_LIFETIME", default=1)),
    "UPDATE_LAST_LOGIN": True,
}

ROOT_URLCONF = 'pop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pop.wsgi.application'


# Database(s)
DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.postgresql',
        "NAME": env("POSTGRES_DATABASE"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "WEBAPP_HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    },
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en-us'         # US English
TIME_ZONE = 'Europe/Berlin'     # Central European time
USE_I18N = True                 # Enable Django’s translation system
USE_TZ = True                   # Do not make datetimes timezone-aware by default


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'                                             # URL to use when referring to static files located in STATIC_ROOT
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]           # Additional locations the staticfiles app will traverse
STATIC_ROOT = '/app/static' # Absolute path to the directory where collectstatic will collect static files for deployment.
MEDIA_ROOT = '/app/media'      # Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_URL = '/media/'                                               # URL that handles the media served from MEDIA_ROOT, used for managing stored files

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logger settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(levelname)s %(asctime)s]: "%(message)s"',
            'datefmt' : '%d/%b/%Y %H:%M:%S',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': { 
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filters': [],
            'filename': '../logs/logfile.log',
            'when': 'midnight',
            'backupCount': 31,
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        }, 
    }
}
