# testsettings.py
from pop.settings import *

INSTALLED_APPS += [
    'pop.tests',
]

PGHISTORY_INSTALL_CONTEXT_FUNC_ON_MIGRATE=True