from functools import wraps
from django.db.models import Model as DjangoModel, Value
from pop.core.auth import permissions
from ninja import Schema
from ninja.errors import HttpError
from typing import Callable, Any


def anonymize():
    """
    Decorator to add an anonymized=True kwarg to a view function and
    enforce permission checks on de-anonymized data access.
    """

    def _decorator(func: Callable) -> Callable:
        @wraps(func)
        def func_wrapper(self, *args, anonymized: bool = True, **kwargs) -> Any:

            user = getattr(
                getattr(getattr(self, "context", None), "request", None), "user", None
            )
            if (
                not anonymized
                and not permissions.CanManageCases().check_user_permission(user)
            ):
                raise HttpError(403, "Permission denied to access pseudonymized data")

            # Call the original function with anonymized kwarg
            result = func(self, *args, anonymized=anonymized, **kwargs)

            if anonymized:
                if isinstance(result, (DjangoModel, Schema)):
                    result.anonymized = True
                elif isinstance(result, (tuple, list)):
                    for res in result:
                        res.anonymized = True
                else:
                    result = result.annotate(anonymized=Value(True))
            return result

        return func_wrapper

    return _decorator
