import pghistory.middleware
from django.db import connection


from django.core.handlers.asgi import ASGIRequest as DjangoASGIRequest
from django.core.handlers.wsgi import WSGIRequest as DjangoWSGIRequest
from django.db import connection

import pghistory
from pghistory import config

class DjangoRequest:
    """
    Although Django's auth middleware sets the user in middleware,
    apps like django-rest-framework set the user in the view layer.
    This creates issues for pghistory tracking since the context needs
    to be set before DB operations happen.

    This special WSGIRequest updates pghistory context when
    the request.user attribute is updated.
    """

    def __setattr__(self, attr, value):
        if attr == "user":
            user = (
                value._meta.pk.get_db_prep_value(value.pk, connection)
                if value and hasattr(value, "_meta")
                else None
            )
            username = (
                value.username if hasattr(value, "username") else None
            )
            pghistory.context(username=username, user=user)
        return super().__setattr__(attr, value)

class WSGIRequest(DjangoRequest, DjangoWSGIRequest):
    pass


class ASGIRequest(DjangoRequest, DjangoASGIRequest):
    pass

class HistoryMiddleware(pghistory.middleware.HistoryMiddleware):

    def get_context(self, request):
        return super().get_context(request) | {
            "username": request.user.username if hasattr(request, "username") else None,
            "ip_address": request.META.get('REMOTE_ADDR', 'unknown'),
        }

    def __call__(self, request):
        if request.method in config.middleware_methods():
            with pghistory.context(**self.get_context(request)):
                if isinstance(request, DjangoWSGIRequest):  # pragma: no branch
                    request.__class__ = WSGIRequest
                elif isinstance(request, DjangoASGIRequest):  # pragma: no cover
                    request.__class__ = ASGIRequest

                return self.get_response(request)
        else:
            return self.get_response(request)