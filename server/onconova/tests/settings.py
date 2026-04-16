# testsettings.py
import pgtrigger

from onconova.settings import *
import factory.random

# Ensure a consistent factory engine
factory.random.reseed_random("onconova-test")

INSTALLED_APPS += [
    "onconova.tests",
]

PGHISTORY_INSTALL_CONTEXT_FUNC_ON_MIGRATE = True

ACCOUNT_RATE_LIMITS = False
NINJA_PAGINATION_PER_PAGE = 100
NINJA_PAGINATION_MAX_LIMIT = 100

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
