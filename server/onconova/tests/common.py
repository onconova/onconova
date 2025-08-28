import uuid
from copy import deepcopy
from typing import List, Type
from urllib.parse import urlencode

import pghistory
import pghistory.models
import pytest
from django.db import connection
from django.db.models.base import ModelBase
from django.test import Client, TestCase
from factory.django import DjangoModelFactory
from faker import Faker
from parameterized import parameterized

from onconova.core.auth.models import User
from onconova.core.models import BaseModel
from onconova.core.serialization.metaclasses import ModelCreateSchema, ModelGetSchema
from onconova.tests.factories import UserFactory, factory


class AbstractModelMixinTestCase(TestCase):
    """
    Abstract test case for mixin class.
    """

    mixin: type
    model: ModelBase

    @classmethod
    def setUpClass(cls) -> None:
        """Create a test model from the mixin"""

        class Meta:
            """Meta options for the temporary model"""

            app_label = "test"

        cls.model = ModelBase(
            "Test" + cls.mixin.__name__,
            (cls.mixin,),
            {
                "__module__": cls.mixin.__module__,
                "Meta": Meta,
            },
        )

        with connection.schema_editor() as editor:
            editor.create_model(cls.model)

        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        """Delete the test model"""
        super().tearDownClass()

        with connection.schema_editor() as editor:
            editor.delete_model(cls.model)

        connection.close()


HTTP_SCENARIOS = [
    (
        "HTTPS Authenticated",
        dict(
            expected_responses=(200, 204, 201),
            authenticated=True,
            use_https=True,
            access_level=4,
        ),
    ),
    (
        "HTTP Authenticated",
        dict(
            expected_responses=(301,),
            authenticated=True,
            use_https=False,
            access_level=4,
        ),
    ),
    (
        "HTTPS Unauthenticated",
        dict(
            expected_responses=(401,),
            authenticated=False,
            use_https=True,
            access_level=4,
        ),
    ),
    (
        "HTTP Unauthenticated",
        dict(
            expected_responses=(301,),
            authenticated=False,
            use_https=False,
            access_level=4,
        ),
    ),
    (
        "HTTPS Unauthorized",
        dict(
            expected_responses=(403,),
            authenticated=True,
            use_https=True,
            access_level=1,
        ),
    ),
]
GET_HTTP_SCENARIOS = HTTP_SCENARIOS[:-1]


class ApiControllerTestMixin:

    # Properties
    controller_path: str
    scenarios = [
        (
            "HTTPS Authenticated",
            dict(
                expected_responses=(200, 204, 201),
                authenticated=True,
                use_https=True,
                access_level=4,
            ),
        ),
        (
            "HTTP Authenticated",
            dict(
                expected_responses=(301,),
                authenticated=True,
                use_https=False,
                access_level=4,
            ),
        ),
        (
            "HTTPS Unauthenticated",
            dict(
                expected_responses=(401,),
                authenticated=False,
                use_https=True,
                access_level=4,
            ),
        ),
        (
            "HTTP Unauthenticated",
            dict(
                expected_responses=(301,),
                authenticated=False,
                use_https=False,
                access_level=4,
            ),
        ),
        (
            "HTTPS Unauthorized",
            dict(
                expected_responses=(403,),
                authenticated=True,
                use_https=True,
                access_level=1,
            ),
        ),
    ]
    get_scenarios = scenarios[:-1]

    faker = Faker()

    @classmethod
    def setUpTestData(cls):
        cls.maxDiff = None
        # Generate user credentials
        username = f"user-{uuid.uuid4()}"
        password = cls.faker.password()
        # Create a fake user with known credentials if not exists
        cls.user: User = User.objects.filter(
            username=username
        ).first() or UserFactory.create(username=username)
        cls.user.set_password(password)
        cls.user.save()
        # Authenticate user and get authentication HTTP header
        cls.auth_header = cls._authenticate_user_and_get_authentication_header(
            username, password
        )
        cls.authenticated_client = Client(headers=cls.auth_header)
        cls.unauthenticated_client = Client()

    def get_route_url(self, instance):
        return f""

    def get_route_url_with_id(self, instance):
        return f"/{instance.id}"

    def get_route_url_history(self, instance):
        return f"/{instance.id}/history/events"

    def get_route_url_history_with_id(self, instance, event):
        return f"/{instance.id}/history/events/{event.pgh_id}"

    def get_route_url_history_revert(self, instance, event):
        return f"/{instance.id}/history/events/{event.pgh_id}/reversion"

    @staticmethod
    def _authenticate_user_and_get_authentication_header(username, password):
        auth_client = Client()
        response = auth_client.post(
            "/api/v1/auth/session",
            data={"username": username, "password": password},
            content_type="application/json",
            secure=True,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Failed to authenticate user. Login endpoint returned {response.status_code}"
            )
        token = response.json()["sessionToken"]
        return {"X-Session-Token": str(token)}

    def call_api_endpoint(
        self,
        verb,
        route,
        expected_responses,
        authenticated,
        use_https,
        access_level,
        anonymized=None,
        data=None,
    ):
        # Set the user access level for this call
        self.user.access_level = access_level
        self.user.save()
        # Prepare the controller
        client = (
            self.authenticated_client if authenticated else self.unauthenticated_client
        )
        action = {
            "POST": client.post,
            "GET": client.get,
            "PUT": client.put,
            "DELETE": client.delete,
        }
        queryparams = (
            f'?{urlencode({"anonymized": anonymized})}'
            if verb == "GET" and anonymized is not None
            else ""
        )
        response = action[verb](
            f"{self.controller_path}{route}" + queryparams,
            secure=use_https,
            data=data if data is not None else None,
            content_type="application/json",
        )
        # Assert that there were no errors
        if response.status_code == 500:
            raise RuntimeError(
                f"An error ocurred during the API call (returned 500): {response.content}"
            )

        # Assert response status code
        assert (
            response.status_code in expected_responses
        ), f"Endpoint responded with {response.status_code} (expected any of {expected_responses})"
        return response


class CrudApiControllerTestCase(ApiControllerTestMixin, TestCase):

    # Public interface
    FACTORY: type[DjangoModelFactory] | List[type[DjangoModelFactory]]
    factories: List[type[DjangoModelFactory]]
    MODEL: Type[BaseModel] | List[Type[BaseModel]]
    SCHEMA: Type[ModelGetSchema] | List[Type[ModelGetSchema]]
    CREATE_SCHEMA: Type[ModelCreateSchema] | List[Type[ModelCreateSchema]]
    history_tracked: bool = True

    # Internal state
    models: List[Type[BaseModel]]
    schemas: List[Type[ModelGetSchema]]
    create_schemas: List[Type[ModelCreateSchema]]

    __test__ = False  # Prevent pytest from collecting this base class as a test

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Ensure subclasses are collected as tests
        cls.__test__ = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Ensure class settings are iterable
        cls.factories = (
            [cls.FACTORY] if not isinstance(cls.FACTORY, list) else cls.FACTORY
        )
        cls.subtests = len(cls.factories)
        cls.models = (
            [cls.MODEL] * cls.subtests if not isinstance(cls.MODEL, list) else cls.MODEL
        )
        cls.schemas = (
            [cls.SCHEMA] * cls.subtests
            if not isinstance(cls.SCHEMA, list)
            else cls.SCHEMA
        )
        cls.create_schemas = (
            [cls.CREATE_SCHEMA] * cls.subtests
            if not isinstance(cls.CREATE_SCHEMA, list)
            else cls.CREATE_SCHEMA
        )
        cls.instances = []
        cls.create_payloads = []
        cls.update_payloads = []
        for factory, schema in zip(cls.factories, cls.create_schemas):
            with pghistory.context(username=cls.user.username):
                instance1, instance2 = factory.create_batch(2)
                cls.instances.append(instance1)
                cls.create_payloads.append(
                    schema.model_validate(instance1).model_dump(mode="json")
                )
                cls.update_payloads.append(
                    schema.model_validate(instance2).model_dump(mode="json")
                )
                instance2.delete()

    def _remove_key_recursive(self, dictionary, keys_to_remove):
        """
        Recursively removes keys from a dictionary that may contain lists.

        Args:
            dictionary (dict): The dictionary to remove the keys from.
            keys_to_remove (list): The list of keys to remove.

        Returns:
            dict: The updated dictionary with the keys removed.
        """

        def __remove_key_recursive(d, key_to_remove):
            for key, value in list(d.items()):
                if key == key_to_remove:
                    del d[key]
                elif isinstance(value, dict):
                    __remove_key_recursive(value, key_to_remove)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            __remove_key_recursive(item, key_to_remove)
            return d

        for key_to_remove in keys_to_remove:
            dictionary = __remove_key_recursive(dictionary, key_to_remove)
        return dictionary

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_get_all(self, scenario, config):
        for i in range(self.subtests):
            can_be_anonymized = hasattr(self.schemas[i], "anonymized")
            instance = self.instances[i]
            # Call the API endpoint
            response = self.call_api_endpoint(
                "GET", self.get_route_url(instance), anonymized=False, **config
            )
            with self.subTest(i=i):
                # Assert response content
                if scenario == "HTTPS Authenticated":
                    self.assertEqual(response.status_code, 200)
                    if "items" in response.json():
                        entry = next(
                            (
                                item
                                for item in response.json()["items"]
                                if str(instance.id) == item["id"]
                            )
                        )
                    else:
                        entry = response.json()[0]
                    expected = self.schemas[i].model_validate(instance).model_dump()
                    result = self.schemas[i].model_validate(entry).model_dump()
                    if self.history_tracked:
                        expected["createdAt"] = expected["createdAt"].replace(
                            microsecond=0
                        )
                        result["createdAt"] = result["createdAt"].replace(microsecond=0)
                    self.assertDictEqual(expected, result)

                    if can_be_anonymized:
                        anonymized_response = self.call_api_endpoint(
                            "GET",
                            self.get_route_url(instance),
                            anonymized=True,
                            **config,
                        )
                        self.assertEqual(anonymized_response.status_code, 200)
                        if "items" in response.json():
                            anonymized_entry = next(
                                (
                                    item
                                    for item in anonymized_response.json()["items"]
                                    if str(instance.id) == item["id"]
                                )
                            )
                        else:
                            anonymized_entry = anonymized_response.json()[0]
                        anonymized_result = (
                            self.schemas[i]
                            .model_validate(anonymized_entry)
                            .model_dump()
                        )
                        if self.history_tracked:
                            anonymized_result["createdAt"] = anonymized_result[
                                "createdAt"
                            ].replace(microsecond=0)
                        self.assertNotEqual(result, anonymized_result)

                self.models[i].objects.all().delete()

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_get_by_id(self, scenario, config):
        for i in range(self.subtests):
            can_be_anonymized = hasattr(self.schemas[i], "anonymized")
            instance = self.instances[i]
            # Call the API endpoint
            response = self.call_api_endpoint(
                "GET", self.get_route_url_with_id(instance), anonymized=False, **config
            )
            with self.subTest(i=i):
                # Assert response content
                if scenario == "HTTPS Authenticated":
                    self.assertEqual(response.status_code, 200)
                    expected = self.schemas[i].model_validate(instance).model_dump()
                    result = (
                        self.schemas[i].model_validate(response.json()).model_dump()
                    )
                    if self.history_tracked:
                        expected["createdAt"] = expected["createdAt"].replace(
                            microsecond=0
                        )
                        result["createdAt"] = result["createdAt"].replace(microsecond=0)
                    self.assertDictEqual(result, expected)

                    if can_be_anonymized:
                        anonymized_response = self.call_api_endpoint(
                            "GET",
                            self.get_route_url_with_id(instance),
                            anonymized=True,
                            **config,
                        )
                        self.assertEqual(anonymized_response.status_code, 200)
                        anonymized_result = (
                            self.schemas[i]
                            .model_validate(anonymized_response.json())
                            .model_dump()
                        )
                        if self.history_tracked:
                            anonymized_result["createdAt"] = anonymized_result[
                                "createdAt"
                            ].replace(microsecond=0)
                        self.assertNotEqual(result, anonymized_result)

                self.models[i].objects.all().delete()

    @parameterized.expand(HTTP_SCENARIOS)
    def test_delete(self, scenario, config):
        for i in range(self.subtests):
            instance = self.instances[i]
            # Call the API endpoint
            response = self.call_api_endpoint(
                "DELETE", self.get_route_url_with_id(instance), **config
            )
            with self.subTest(i=i):
                # Assert response content
                if scenario == "HTTPS Authenticated":
                    self.assertEqual(response.status_code, 204)
                    self.assertFalse(
                        self.models[i].objects.filter(id=instance.id).exists()
                    )
                    # Assert audit trail
                    if self.history_tracked:
                        self.assertTrue(
                            pghistory.models.Events.objects.filter(
                                pgh_obj_id=instance.id, pgh_label="delete"
                            ).exists(),
                            "Event not properly registered",
                        )
                self.models[i].objects.all().delete()

    @parameterized.expand(HTTP_SCENARIOS)
    def test_create(self, scenario, config):
        for i, (instance, payload, model) in enumerate(
            zip(self.instances, self.create_payloads, self.models)
        ):
            instance.delete()
            # Call the API endpoint.
            response = self.call_api_endpoint(
                "POST", self.get_route_url(instance), data=payload, **config
            )
            with self.subTest(i=i):
                # Assert response content
                if scenario == "HTTPS Authenticated":
                    created_id = response.json()["id"]
                    created_instance = model.objects.filter(id=created_id).first()
                    assert created_instance is not None, "Resource has not been created"
                    # Assert audit trail
                    if self.history_tracked:
                        self.assertEqual(
                            self.user.username,
                            created_instance.created_by,
                            "Unexpected creator user.",
                        )
                        self.assertTrue(
                            created_instance.events.filter(pgh_label="create").exists(),  # type: ignore
                            "Event not properly registered",
                        )
                model.objects.all().delete()

    @parameterized.expand(HTTP_SCENARIOS)
    def test_update(self, scenario, config):
        if not getattr(self, "HAS_UPDATE_ENDPOINT", True):
            pytest.skip("No relevant endpoint")
        for i in range(self.subtests):
            instance = self.instances[i]
            payload = self.update_payloads[i]
            with self.subTest(i=i):
                # Call the API endpoint
                response = self.call_api_endpoint(
                    "PUT", self.get_route_url_with_id(instance), data=payload, **config
                )
                # Assert response content
                if scenario == "HTTPS Authenticated":
                    updated_id = response.json()["id"]
                    self.assertEqual(response.status_code, 200)
                    updated_instance = (
                        self.models[i].objects.filter(id=updated_id).first()
                    )
                    assert (
                        updated_instance is not None
                    ), "The updated instance does not exist"
                    self.assertNotEqual(
                        [
                            getattr(instance, field.name)
                            for field in self.models[i]._meta.concrete_fields
                        ],
                        [
                            getattr(updated_instance, field.name)
                            for field in self.models[i]._meta.concrete_fields
                        ],
                    )
                    # Assert audit trail
                    if self.history_tracked:
                        if updated_instance.updated_by:
                            self.assertIn(
                                self.user.username,
                                updated_instance.updated_by,  # type: ignore
                                "The updating user is not registered",
                            )
                        self.assertTrue(
                            pghistory.models.Events.objects.filter(
                                pgh_obj_id=instance.id, pgh_label="update"
                            ).exists(),
                            "Event not properly registered",
                        )
                self.models[i].objects.all().delete()

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_get_all_history_events(self, scenario, config):
        for i in range(self.subtests):
            if not hasattr(self.models[i], "pgh_event_model"):
                pytest.skip("Non-tracked model")
            instance = self.instances[i]
            # Call the API endpoint
            response = self.call_api_endpoint(
                "GET", self.get_route_url_history(instance), **config
            )
            with self.subTest(i=i):
                # Assert response content
                if scenario == "HTTPS Authenticated":
                    self.assertEqual(response.status_code, 200)
                    entry = next((item for item in response.json()["items"]))
                    self.assertEqual(entry["category"], "create")
                    self.assertEqual(entry["user"], self.user.username)
                    self.assertEqual(entry["snapshot"]["id"], str(instance.id))
                self.models[i].objects.all().delete()

    @parameterized.expand(GET_HTTP_SCENARIOS)
    def test_get_history_events_by_id(self, scenario, config):
        for i in range(self.subtests):
            if not hasattr(self.models[i], "pgh_event_model"):
                pytest.skip("Non-tracked model")
            instance = self.instances[i]
            if hasattr(instance, "parent_events"):
                event = instance.parent_events.first()
            else:
                event = instance.events.first()
            # Call the API endpoint
            response = self.call_api_endpoint(
                "GET", self.get_route_url_history_with_id(instance, event), **config
            )
            with self.subTest(i=i):
                # Assert response content
                if scenario == "HTTPS Authenticated":
                    self.assertEqual(response.status_code, 200)
                    entry = response.json()
                    self.assertEqual(entry["id"], event.pgh_id)
                    self.assertEqual(entry["user"], event.pgh_context["username"])
                    self.assertEqual(entry["snapshot"]["id"], str(instance.id))
                self.models[i].objects.all().delete()

    @parameterized.expand(HTTP_SCENARIOS)
    def test_revert_changes(self, scenario, config):
        for i in range(self.subtests):
            if not hasattr(self.models[i], "pgh_event_model"):
                pytest.skip("Non-tracked model")
            original_instance = self.instances[i]
            original_instance = (
                self.models[i].objects.filter(pk=original_instance.pk).first()
            )
            payload = self.update_payloads[i]
            updated_instance = (
                self.create_schemas[i]
                .model_validate(payload)
                .model_dump_django(instance=deepcopy(original_instance))
            )
            if hasattr(original_instance, "parent_events"):
                insert_event = original_instance.parent_events.filter(  # type: ignore
                    pgh_label="create"
                ).first()
            else:
                insert_event = original_instance.events.filter(  # type: ignore
                    pgh_label="create"
                ).first()
            response = self.call_api_endpoint(
                "PUT",
                self.get_route_url_history_revert(original_instance, insert_event),
                **config,
            )
            with self.subTest(i=i):
                # Assert response content
                if scenario == "HTTPS Authenticated":
                    updated_id = response.json()["id"]
                    reverted_instance = (
                        self.models[i].objects.filter(id=updated_id).first()
                    )
                    self.assertIsNotNone(
                        reverted_instance, "The updated instance does not exist"
                    )
                    self.assertNotEqual(
                        [
                            getattr(original_instance, field.name)
                            for field in self.models[i]._meta.concrete_fields
                        ],
                        [
                            getattr(updated_instance, field.name)
                            for field in self.models[i]._meta.concrete_fields
                        ],
                    )
                    self.assertNotEqual(
                        [
                            getattr(reverted_instance, field.name)
                            for field in self.models[i]._meta.concrete_fields
                        ],
                        [
                            getattr(updated_instance, field.name)
                            for field in self.models[i]._meta.concrete_fields
                        ],
                    )
                    self.assertEqual(
                        [
                            getattr(reverted_instance, field.name)
                            for field in self.models[i]._meta.concrete_fields
                        ],
                        [
                            getattr(original_instance, field.name)
                            for field in self.models[i]._meta.concrete_fields
                        ],
                    )
                self.models[i].objects.all().delete()


#

#
