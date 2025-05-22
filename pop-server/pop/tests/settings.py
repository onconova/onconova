# testsettings.py
from pop.settings import *
import pgtrigger 

INSTALLED_APPS += [
    'pop.tests',
]

PGHISTORY_INSTALL_CONTEXT_FUNC_ON_MIGRATE=True

ACCOUNT_RATE_LIMITS = False
