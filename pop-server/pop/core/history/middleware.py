import base64
import gzip
import json
import logging
import time

import pghistory
import pghistory.middleware
from django.core.handlers.asgi import ASGIRequest as DjangoASGIRequest
from django.core.handlers.wsgi import WSGIRequest as DjangoWSGIRequest
from django.db import connection
from pghistory import config

SENSITIVE_KEYS = ["password", "token", "secret", "access_token", "identity_token"]
audit_logger = logging.getLogger("audit")


class AuditLogMiddleware:
    """
    Middleware that logs detailed audit information for each HTTP request and response.

    This middleware captures and logs the following information:
    - User identification (ID, username, access level), or marks as anonymous if unauthenticated.
    - Request metadata such as IP address, HTTP method, endpoint path, user agent, and processing duration.
    - Request and response data, with sensitive fields redacted and optionally compressed and base64-encoded.
    - HTTP status code of the response.

    Sensitive fields in request and response data are redacted based on a predefined list of keys.
    Handles both JSON and non-JSON responses gracefully, and ensures that unreadable or non-JSON data is marked accordingly.

    Args:
        get_response (callable): The next middleware or view in the Django request/response chain.

    Methods:
        __call__(request): Processes the request, logs audit information, and returns the response.
        get_request_data(request): Extracts and redacts request data, handling JSON and query parameters.
        get_response_data(response): Extracts and redacts response data, handling JSON and non-JSON responses.
        redact(data): Recursively redacts sensitive fields in dictionaries and lists.
        compress_b64(data): Compresses and base64-encodes a string, handling errors gracefully.
        get_client_ip(request): Retrieves the client's IP address from request headers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        processing_time = round((time.time() - start_time) * 1000)

        user = getattr(request, "user", None)
        user_id = str(user.id) if user and user.is_authenticated else "anonymous"
        user_access_level = (
            int(user.access_level) if user and user.is_authenticated else -1
        )
        username = str(user.username) if user and user.is_authenticated else "anonymous"
        endpoint = request.get_full_path()
        audit_logger.info(
            "",
            extra={
                "user_id": user_id,
                "username": username,
                "access_level": user_access_level,
                "ip": self.get_client_ip(request),
                "method": request.method,
                "duration": processing_time,
                "path": endpoint,
                "status_code": response.status_code,
                "user_agent": request.META.get("HTTP_USER_AGENT", "")[:100],
                "request_data": (
                    self.compress_b64(self.get_request_data(request))
                    if "openapi.json" not in endpoint
                    else "[openapi.json]"
                ),
                "response_data": (
                    self.compress_b64(self.get_response_data(response))
                    if "openapi.json" not in endpoint
                    else "[openapi.json]"
                ),
            },
        )
        return response

    def get_request_data(self, request):
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                if request.body:
                    body = request.body.decode("utf-8")
                    data = json.loads(body)
                    return json.dumps(self.redact(data), separators=(",", ":"))
            return json.dumps(self.redact(request.GET.dict()), separators=(",", ":"))
        except Exception as e:
            audit_logger.exception(e)
            return "[unreadable]"

    def get_response_data(self, response):
        try:
            if hasattr(response, "data"):
                return json.dumps(self.redact(response.data), separators=(",", ":"))
            content_type = response.get("Content-Type", "")
            if "application/json" in content_type:
                return response.content.decode("utf-8")
            return "[non-json-response]"
        except Exception as e:
            audit_logger.exception(e)
            return "[unreadable]"

    @staticmethod
    def redact(data) -> object:
        if isinstance(data, dict):
            redacted = {}
            for k, v in data.items():
                if any(s in k.lower() for s in SENSITIVE_KEYS):
                    redacted[k] = "[REDACTED]"
                else:
                    redacted[k] = AuditLogMiddleware.redact(v)
            return redacted
        elif isinstance(data, list):
            return [AuditLogMiddleware.redact(item) for item in data]
        else:
            return data

    @staticmethod
    def compress_b64(data: str) -> str:
        try:
            compressed = gzip.compress(bytes(data, "utf-8"))
            return base64.b64encode(compressed).decode("utf-8")
        except Exception:
            return "[compress-error]"

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        return (
            x_forwarded_for.split(",")[0]
            if x_forwarded_for
            else request.META.get("REMOTE_ADDR")
        )


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
                str(value._meta.pk.get_db_prep_value(value.pk, connection))
                if value and hasattr(value, "_meta")
                else None
            )
            username = value.username if hasattr(value, "username") else None
            pghistory.context(username=username, user=user)
        return super().__setattr__(attr, value)


class WSGIRequest(DjangoRequest, DjangoWSGIRequest):
    pass


class ASGIRequest(DjangoRequest, DjangoASGIRequest):
    pass


class HistoryMiddleware(pghistory.middleware.HistoryMiddleware):

    def get_context(self, request):
        return super().get_context(request) | {
            "username": (
                request.user.username if hasattr(request.user, "username") else None
            ),
            "ip_address": request.META.get("REMOTE_ADDR", "unknown"),
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
