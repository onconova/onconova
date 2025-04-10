from django.test import TestCase
from unittest.mock import MagicMock, patch
from io import BytesIO

from django.core.handlers.wsgi import WSGIRequest as DjangoWSGIRequest
from django.core.handlers.asgi import ASGIRequest as DjangoASGIRequest
from django.http import HttpRequest

from pop.core.middleware import HistoryMiddleware, WSGIRequest, ASGIRequest, DjangoRequest


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

        mock_context.assert_called_once_with(username="alice", user=1)


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
        req.user = MockUser(pk=2, username="bob")
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
        req.user = MockUser(pk=3, username="charlie")
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
