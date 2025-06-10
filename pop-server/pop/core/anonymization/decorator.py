
from functools import wraps
from django.db.models import Model as DjangoModel, Value
from pop.core import permissions
from ninja import Schema

def anonymize():
    """
    Decorator to add anonymized=True kwarg and check permission on output.
    """
    def _decorator(func):
        @wraps(func)
        def func_wrapper(self, *args, anonymized=True, **kwargs):
            # Call the original function with anonymized kwarg
            result = func(self, *args, anonymized=anonymized, **kwargs)

            user = getattr(getattr(getattr(self, 'context', None), 'request', None), 'user', None)

            if anonymized:
                if not permissions.CanManageCases().check_user_permission(user):
                    raise HttpError(403, "Permission denied to access de-anonymized data")
                if isinstance(result, (DjangoModel,Schema)):
                    result.anonymized = True 
                elif isinstance(result, (tuple, list)):
                    for res in result:
                        res.anonymized = True 
                else:
                    result = result.annotate(anonymized=Value(True))
            return result
        
        return func_wrapper
    
    return _decorator