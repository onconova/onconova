# testsettings.py
import pgtrigger

from onconova.settings import *

INSTALLED_APPS += [
    "onconova.tests",
]

PGHISTORY_INSTALL_CONTEXT_FUNC_ON_MIGRATE = True

ACCOUNT_RATE_LIMITS = False


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
