import pytest
from django.conf import settings
from django.core.management import call_command
from pytest_django.fixtures import _disable_migrations
import logging


# Enable access to the test database to all tests by default
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
