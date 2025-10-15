from unittest.mock import MagicMock, patch

import pghistory
from django.test import Client, TestCase
from faker import Faker
from parameterized import parameterized

from onconova.core.auth.models import User as UserORM
from onconova.core.auth.schemas import (
    UserCreate,
    UserPasswordReset,
    UserProfile,
    User,
)
from onconova.core.history.schemas import HistoryEvent
from onconova.core.measures import measures
from onconova.core.measures.schemas import MeasureConversion
from onconova.tests import factories
from onconova.tests.common import (
    GET_HTTP_SCENARIOS,
    HTTP_SCENARIOS,
    ApiControllerTestMixin,
)


class TestAuthController(ApiControllerTestMixin, TestCase):
    controller_path = "/api/users"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Generate user credentials
        cls.username = f"testuser"
        cls.password = Faker().password()
        cls.email = Faker().email()
        # Create a fake user with known credentials if not exists
        user = factories.UserFactory.create(username=cls.username, email=cls.email)
        user.set_password(cls.password)
        user.save()

    def test_login_user_with_username_password(self):
        client = Client()
        response = client.post(
            "/api/v1/auth/session",
            data={"username": self.username, "password": self.password},
            content_type="application/json",
            secure=True,
        )
        self.assertTrue(response.status_code, 200)
        self.assertIn("sessionToken", response.json())

    def test_login_user_with_email_password(self):
        client = Client()
        response = client.post(
            "/api/v1/auth/session",
            data={"username": self.email, "password": self.password},
            content_type="application/json",
            secure=True,
        )
        self.assertTrue(response.status_code, 200)
        self.assertIn("sessionToken", response.json())

    def test_login_user_with_provider_token(self):
        client = Client()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = (
            b'{"meta": {"isAuthenticated": "True", "sessionToken": "12345678"}}'
        )
        mock_view_func = MagicMock(return_value=mock_response)
        with patch(
            "onconova.core.auth.controllers.resolve",
            return_value=MagicMock(func=mock_view_func),
        ) as mock_redirect:
            response = client.post(
                "/api/v1/auth/provider/session",
                data={
                    "provider": "providerId",
                    "process": "login",
                    "token": {
                        "client_id": "clientId",
                        "id_token": "12345678",
                    },
                },
                content_type="application/json",
                secure=True,
            )
            mock_redirect.assert_called_once()
            self.assertTrue(response.status_code, 200)
            self.assertIn("sessionToken", response.json())


class TestUserController(ApiControllerTestMixin, TestCase):
    controller_path = "/api/v1/users"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.instance = factories.UserFactory()

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_get_all_users(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET", self.get_route_url(self.instance), **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            entry = response.json()["items"][0]
            # Assert response content
            expected = User.model_validate(self.instance).model_dump()
            result = User.model_validate(entry).model_dump()
            self.assertEqual(expected, result)

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_get_user_by_id(self, scenario, config):
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET", self.get_route_url_with_id(self.instance), **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            entry = response.json()
            # Assert response content
            expected = User.model_validate(self.instance).model_dump()
            result = User.model_validate(entry).model_dump()
            self.assertEqual(expected, result)

    @parameterized.expand(HTTP_SCENARIOS)
    def test_create_user_by_id(self, scenario, config):
        json_data = UserCreate.model_validate(self.instance).model_dump(
            mode="json"
        )
        json_data["username"] = "new_username"
        # Call the API endpoint.
        response = self.call_api_endpoint(
            "POST", self.get_route_url(self.instance), data=json_data, **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            new_user = UserORM.objects.get(id=response.json()["id"])
            self.assertEqual("new_username", new_user.username)

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_get_user_events(self, scenario, config):
        with pghistory.context(username=self.user.username):
            resource = factories.PatientCaseFactory.create()
        # Call the API endpoint
        response = self.call_api_endpoint("GET", f"/{self.user.id}/events", **config)
        # Assert response content
        if scenario == "HTTPS Authenticated":
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            events = response.json()["items"]
            # Assert response content
            for event in zip(events):
                self.assertTrue(resource.events.filter(pgh_id=event[0]["id"]).exists())

    @parameterized.expand(HTTP_SCENARIOS)
    def test_update_user_and_access_level(self, scenario, config):
        update_schema = UserCreate.model_validate(self.instance)
        update_schema.accessLevel = 4
        json_data = update_schema.model_dump(mode="json")
        # Call the API endpoint.
        response = self.call_api_endpoint(
            "PUT", self.get_route_url_with_id(self.instance), data=json_data, **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            updated_instance = UserORM.objects.get(id=response.json()["id"])
            self.assertEqual(updated_instance.access_level, 4)

    @parameterized.expand(HTTP_SCENARIOS)
    def test_update_user_profile(self, scenario, config):
        new_first_name = "John"
        new_last_name = "Doe"
        json_data = UserProfile(
            firstName=new_first_name,
            lastName=new_last_name,
            email=self.instance.email,
        ).model_dump(mode="json")
        # Call the API endpoint.
        response = self.call_api_endpoint(
            "PUT", f"/{self.instance.id}/profile", data=json_data, **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            updated_instance = UserORM.objects.get(id=response.json()["id"])
            self.assertEqual(updated_instance.first_name, new_first_name)
            self.assertEqual(updated_instance.last_name, new_last_name)

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_update_own_profile(self, scenario, config):
        new_config = {**config, "access_level": 1}
        new_first_name = "John"
        new_last_name = "Doe"
        json_data = UserProfile(
            firstName=new_first_name, lastName=new_last_name, email=self.user.email
        ).model_dump(mode="json")
        # Call the API endpoint.
        self.call_api_endpoint(
            "PUT", f"/{self.user.id}/profile", data=json_data, **new_config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.user.refresh_from_db()
            self.assertEqual(self.user.first_name, new_first_name)
            self.assertEqual(self.user.last_name, new_last_name)

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_update_own_password(self, scenario, config):
        new_config = {**config, "access_level": 1}
        old_password = "oldPassword123"
        new_password = "newPassword123"
        self.user.set_password(old_password)
        self.user.save()
        payload = UserPasswordReset(
            oldPassword=old_password, newPassword=new_password
        ).model_dump(mode="json")
        # Call the API endpoint.
        self.call_api_endpoint(
            "PUT", f"/{self.user.id}/password", data=payload, **new_config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            self.user.refresh_from_db()
            self.assertFalse(self.user.check_password(old_password))
            self.assertTrue(self.user.check_password(new_password))


class TestMeasuresController(ApiControllerTestMixin, TestCase):
    controller_path = "/api/v1/measures"

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_get_measure_units(self, scenario, config):
        measure = measures.Volume
        # Call the API endpoint
        response = self.call_api_endpoint("GET", f"/{measure.__name__}/units", **config)
        # Assert response content
        if scenario == "HTTPS Authenticated":
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            self.assertEqual(list(measure.get_units().keys()), response.json())

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_get_measure_default_units(self, scenario, config):
        measure = measures.Volume
        # Call the API endpoint
        response = self.call_api_endpoint(
            "GET", f"/{measure.__name__}/units/default", **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            # Assert resonse status
            self.assertEqual(response.status_code, 200)
            self.assertEqual(measure.STANDARD_UNIT, response.json())

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_convert_units(self, scenario, config):
        measure = measures.Mass
        data = MeasureConversion(value=1, unit="kg", new_unit="g").model_dump(
            mode="json"
        )
        # Call the API endpoint
        response = self.call_api_endpoint(
            "POST", f"/{measure.__name__}/units/conversion", data=data, **config
        )
        # Assert response content
        if scenario == "HTTPS Authenticated":
            # Assert resonse status
            converted_measure = response.json()
            self.assertEqual(converted_measure["unit"], "g")
            self.assertEqual(converted_measure["value"], 1000)
