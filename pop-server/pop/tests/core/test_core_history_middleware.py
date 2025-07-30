import base64
import gzip
import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.handlers.asgi import ASGIRequest as DjangoASGIRequest
from django.core.handlers.wsgi import WSGIRequest as DjangoWSGIRequest
from django.http import HttpRequest
from django.test import TestCase
from pop.core.history.middleware import (
    ASGIRequest,
    AuditLogMiddleware,
    DjangoRequest,
    HistoryMiddleware,
    WSGIRequest,
)


class MockUser:
    def __init__(self, pk, username="testuser"):
        self.pk = pk
        self.username = username
        self._meta = MagicMock()
        self._meta.pk.get_db_prep_value.return_value = pk


class TestDjangoRequest(TestCase):

    @patch("pghistory.context")
    def test_user_set_sets_pghistory_context(self, mock_context):
        req = DjangoRequest()
        user = MockUser(pk=1, username="alice")

        setattr(req, "user", user)

        mock_context.assert_called_once_with(username="alice", user="1")


class TestHistoryMiddleware(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.get_response = MagicMock(return_value="response")
        cls.middleware = HistoryMiddleware(cls.get_response)

    @patch("pghistory.context")
    @patch("pghistory.config.middleware_methods", return_value=["GET", "POST"])
    def test_middleware_wraps_wsgi_request(self, mock_methods, mock_context):
        scope = {"REQUEST_METHOD": "GET", "wsgi.input": MagicMock()}
        req = DjangoWSGIRequest(scope)
        req.user = MockUser(pk=2, username="bob")  # type: ignore
        req.META["REMOTE_ADDR"] = "127.0.0.1"

        response = self.middleware(req)

        self.assertEqual(response, "response")
        self.assertIsInstance(req, WSGIRequest)
        mock_context.assert_called_once()
        context_args = mock_context.call_args[1]
        self.assertEqual(context_args["ip_address"], "127.0.0.1")

    @patch("pghistory.context")
    @patch("pghistory.config.middleware_methods", return_value=["GET", "POST"])
    def test_middleware_wraps_asgi_request(self, mock_methods, mock_context):
        scope = {
            "type": "http",
            "method": "GET",
            "headers": [],
            "path": "/",
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 12345),
        }
        body_file = BytesIO(b"")

        req = DjangoASGIRequest(scope, body_file)
        req.user = MockUser(pk=3, username="charlie")  # type: ignore
        req.META["REMOTE_ADDR"] = "10.0.0.1"

        response = self.middleware(req)

        self.assertEqual(response, "response")
        self.assertIsInstance(req, ASGIRequest)
        mock_context.assert_called_once()
        context_args = mock_context.call_args[1]
        self.assertEqual(context_args["ip_address"], "10.0.0.1")

    @patch("pghistory.config.middleware_methods", return_value=["GET", "POST"])
    def test_middleware_skips_non_tracked_methods(self, mock_methods):
        request = HttpRequest()
        request.method = "OPTIONS"

        result = self.middleware(request)

        self.assertEqual(result, "response")
        self.assertFalse(isinstance(request, (WSGIRequest, ASGIRequest)))


class DummyUser:
    def __init__(
        self, is_authenticated=True, id=1, username="testuser", access_level=5
    ):
        self.is_authenticated = is_authenticated
        self.id = id
        self.username = username
        self.access_level = access_level


class DummyRequest:
    def __init__(
        self,
        method="GET",
        body=b"",
        user=None,
        META=None,
        GET=None,
        path="/api/test/",
        full_path=None,
    ):
        self.method = method
        self.body = body
        self.user = user
        self.META = META or {}
        self.GET = GET or {}
        self.path = path
        self._full_path = full_path

    def get_full_path(self):
        return self._full_path or self.path


class DummyResponse:
    def __init__(
        self, data=None, content=None, status_code=200, content_type="application/json"
    ):
        self.data = data
        self.content = content or b""
        self.status_code = status_code
        self._headers = {"Content-Type": content_type}

    def get(self, key, default=None):
        return self._headers.get(key, default)


@pytest.fixture
def middleware():
    def dummy_get_response(request):
        return DummyResponse(
            data={"result": "ok"}, content=b'{"result":"ok"}', status_code=200
        )

    return AuditLogMiddleware(dummy_get_response)


def test_redact_removes_sensitive_keys():
    data = {
        "username": "user",
        "password": "secret",
        "token": "abc",
        "nested": {"access_token": "def", "other": "val"},
        "list": [{"secret": "x"}],
    }
    redacted: object = AuditLogMiddleware.redact(data)
    assert isinstance(redacted, dict)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["token"] == "[REDACTED]"
    assert redacted["nested"]["access_token"] == "[REDACTED]"
    assert redacted["nested"]["other"] == "val"
    assert redacted["list"][0]["secret"] == "[REDACTED]"


def test_compress_b64_and_decompress():
    original = '{"foo":"bar"}'
    encoded = AuditLogMiddleware.compress_b64(original)
    # decompress to verify
    decoded = gzip.decompress(base64.b64decode(encoded)).decode("utf-8")
    assert decoded == original


def test_compress_b64_handles_error():
    # Passing a non-string should return "[compress-error]"
    assert AuditLogMiddleware.compress_b64(None) == "[compress-error]"  # type: ignore


def test_get_client_ip_from_x_forwarded_for():
    request = DummyRequest(META={"HTTP_X_FORWARDED_FOR": "1.2.3.4,5.6.7.8"})
    ip = AuditLogMiddleware.get_client_ip(request)
    assert ip == "1.2.3.4"


def test_get_client_ip_from_remote_addr():
    request = DummyRequest(META={"REMOTE_ADDR": "9.8.7.6"})
    ip = AuditLogMiddleware.get_client_ip(request)
    assert ip == "9.8.7.6"


def test_get_request_data_post_json(middleware):
    body = json.dumps({"foo": "bar", "password": "123"}).encode("utf-8")
    request = DummyRequest(method="POST", body=body)
    result = middleware.get_request_data(request)
    assert '"foo":"bar"' in result
    assert '"password":"[REDACTED]"' in result


def test_get_request_data_get_params(middleware):
    class DummyQueryDict(dict):
        def dict(self):
            return dict(self)

    request = DummyRequest(
        method="GET", GET=DummyQueryDict({"token": "abc", "q": "search"})
    )
    result = middleware.get_request_data(request)
    assert '"token":"[REDACTED]"' in result
    assert '"q":"search"' in result


def test_get_request_data_unreadable(middleware):
    # Invalid JSON body
    request = DummyRequest(method="POST", body=b"{notjson")
    result = middleware.get_request_data(request)
    assert result == "[unreadable]"


def test_get_response_data_json(middleware):
    response = DummyResponse(data={"foo": "bar", "secret": "hide"})
    result = middleware.get_response_data(response)
    assert '"foo":"bar"' in result
    assert '"secret":"[REDACTED]"' in result


def test_get_response_data_content_type_json(middleware):
    response = DummyResponse(content=b'{"foo":"bar"}', content_type="application/json")
    delattr(response, "data")
    result = middleware.get_response_data(response)
    assert result == '{"foo":"bar"}'


def test_get_response_data_non_json(middleware):
    response = DummyResponse(content=b"plain text", content_type="text/plain")
    delattr(response, "data")
    result = middleware.get_response_data(response)
    assert result == "[non-json-response]"


def test_get_response_data_unreadable(middleware):
    # Simulate error in decoding
    response = DummyResponse(content=b"\x80", content_type="application/json")
    delattr(response, "data")
    result = middleware.get_response_data(response)
    assert result == "[unreadable]"


@patch("pop.core.history.middleware.audit_logger")
def test_audit_log_middleware_logs_info(audit_logger_mock):
    user = DummyUser()
    body = json.dumps({"foo": "bar", "password": "123"}).encode("utf-8")
    request = DummyRequest(
        method="POST",
        body=body,
        user=user,
        META={"REMOTE_ADDR": "127.0.0.1", "HTTP_USER_AGENT": "pytest-agent"},
        path="/api/test/",
    )

    def get_response(req):
        return DummyResponse(
            data={"result": "ok", "token": "abc"},
            content=b'{"result":"ok","token":"abc"}',
            status_code=201,
        )

    middleware = AuditLogMiddleware(get_response)
    response = middleware(request)
    assert response.status_code == 201
    assert audit_logger_mock.info.called
    log_args, log_kwargs = audit_logger_mock.info.call_args
    extra = log_kwargs["extra"]
    assert extra["user_id"] == str(user.id)
    assert extra["username"] == user.username
    assert extra["access_level"] == user.access_level
    assert extra["ip"] == "127.0.0.1"
    assert extra["method"] == "POST"
    assert extra["status_code"] == 201
    assert extra["user_agent"] == "pytest-agent"
    # request_data and response_data are base64-encoded
    assert isinstance(extra["request_data"], str)
    assert isinstance(extra["response_data"], str)


@patch("pop.core.history.middleware.audit_logger")
def test_audit_log_middleware_anonymous_user(audit_logger_mock):
    request = DummyRequest(
        method="GET",
        user=None,
        META={"REMOTE_ADDR": "127.0.0.1"},
        path="/api/test/",
    )

    def get_response(req):
        return DummyResponse(
            data={"result": "ok"}, content=b'{"result":"ok"}', status_code=200
        )

    middleware = AuditLogMiddleware(get_response)
    response = middleware(request)
    assert response.status_code == 200
    log_args, log_kwargs = audit_logger_mock.info.call_args
    extra = log_kwargs["extra"]
    assert extra["user_id"] == "anonymous"
    assert extra["username"] == "anonymous"
    assert extra["access_level"] == -1


@patch("pop.core.history.middleware.audit_logger")
def test_audit_log_middleware_openapi_json(audit_logger_mock):
    request = DummyRequest(
        method="GET",
        user=None,
        META={"REMOTE_ADDR": "127.0.0.1"},
        path="/api/openapi.json",
    )

    def get_response(req):
        return DummyResponse(
            data={"openapi": "spec"}, content=b'{"openapi":"spec"}', status_code=200
        )

    middleware = AuditLogMiddleware(get_response)
    response = middleware(request)
    log_args, log_kwargs = audit_logger_mock.info.call_args
    extra = log_kwargs["extra"]
    assert extra["request_data"] == "[openapi.json]"
    assert extra["response_data"] == "[openapi.json]"
