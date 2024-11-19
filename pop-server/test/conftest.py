import pytest
from django.conf import settings 
from django.core.management import call_command
from pytest_django.fixtures import _disable_migrations
import logging 


# Enable access to the test database to all tests by default
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

# Setup the test database(s) configuration  
@pytest.fixture(scope='session')
def django_db_setup(    
    request,
    django_test_environment,
    django_db_blocker,
    django_db_use_migrations,
    django_db_keepdb,
    django_db_createdb,
    django_db_modify_db_settings,
):

    # Disable logging during tests
    logging.disable(logging.CRITICAL)

    from django.test.utils import setup_databases, teardown_databases
    setup_databases_args = {}

    if not django_db_use_migrations:
        _disable_migrations()

    if django_db_keepdb and not django_db_createdb:
        setup_databases_args["keepdb"] = True

    with django_db_blocker.unblock():
        db_cfg = setup_databases(
            verbosity=request.config.option.verbose,
            interactive=False,
            **setup_databases_args,
        )

    yield

    if not django_db_keepdb:
        with django_db_blocker.unblock():
            try:
                teardown_databases(db_cfg, verbosity=request.config.option.verbose)
            except Exception as exc:  # noqa: BLE001
                request.node.warn(
                    pytest.PytestWarning(f"Error when trying to teardown test databases: {exc!r}")
                )
