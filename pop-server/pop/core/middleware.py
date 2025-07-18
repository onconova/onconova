import base64
import gzip
import json
import logging
import time

from django.utils.deprecation import MiddlewareMixin
from ninja_extra.logger import request_logger

SENSITIVE_KEYS = ["password", "token", "secret", "access_token", "identity_token"]

audit_logger = logging.getLogger("audit")


class AuditLogMiddleware:
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
        audit_logger.info(
            "",
            extra={
                "user_id": user_id,
                "username": username,
                "access_level": user_access_level,
                "ip": self.get_client_ip(request),
                "method": request.method,
                "duration": processing_time,
                "path": request.get_full_path(),
                "status_code": response.status_code,
                "user_agent": request.META.get("HTTP_USER_AGENT", "")[:100],
                "request_data": self.compress_b64(self.get_request_data(request)),
                "response_data": self.compress_b64(self.get_response_data(response)),
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
            print(e)
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
            print(e)
            return "[unreadable]"

    @staticmethod
    def redact(data: dict) -> dict:
        redacted = {}
        for k, v in data.items():
            if any(s in k.lower() for s in SENSITIVE_KEYS):
                redacted[k] = "[REDACTED]"
            else:
                redacted[k] = v
        return redacted

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
