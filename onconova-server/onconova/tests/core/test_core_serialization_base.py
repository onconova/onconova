import unittest
from datetime import datetime
from uuid import uuid4

from django.db.models import CharField, IntegerField, Model
from pydantic import Field

from onconova.core.anonymization import REDACTED_STRING, AnonymizationMixin
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.core.types import Nullable
from onconova.tests.models import UntrackedMockBaseModel


class TestSchemaAnonymization(unittest.TestCase):

    class TestCreateSchema(ModelCreateSchema):
        config = SchemaConfig(model=UntrackedMockBaseModel)

    class TestGetSchema(ModelGetSchema, AnonymizationMixin):
        identifier: Nullable[str] = Field(default=None)
        date: Nullable[datetime] = Field(default=None)
        caseId: str = Field(default="test")
        config = SchemaConfig(
            model=UntrackedMockBaseModel,
            anonymization=dict(fields=("date", "identifier"), key="caseId"),
        )

    def test_create_model_schema_has_not_anonymized_field(self):
        instance = self.TestCreateSchema(id=uuid4(), description="test")
        self.assertFalse(hasattr(instance, "anonymized"))

    def test_get_model_schema_has_anonymized_field(self):
        instance = self.TestGetSchema(id=uuid4(), description="test")
        self.assertTrue(hasattr(instance, "anonymized"))

    def test_get_model_schema_is_not_anonymized_by_default(self):
        instance = self.TestGetSchema(id=uuid4(), description="test")
        self.assertFalse(instance.anonymized)

    def test_date_is_properly_anonymized(self):
        original_date = datetime(2000, 1, 1)
        instance = self.TestGetSchema(
            id=uuid4(), description="test", date=original_date, anonymized=True
        )
        self.assertNotEqual(instance.date, original_date)

    def test_date_can_be_deanonymized(self):
        original_date = datetime(2000, 1, 1)
        instance = self.TestGetSchema(
            id=uuid4(), description="test", date=original_date, anonymized=False
        )
        self.assertEqual(instance.date, original_date)

    def test_relative_dates_are_preserved_when_anonymized(self):
        original_date1 = datetime(2000, 1, 1)
        original_date2 = datetime(2000, 2, 2)
        instance1 = self.TestGetSchema(
            id=uuid4(), description="test", date=original_date1, anonymized=True
        )
        instance2 = self.TestGetSchema(
            id=uuid4(), description="test", date=original_date2, anonymized=True
        )
        self.assertNotEqual(instance1.date, original_date1)
        self.assertNotEqual(instance2.date, original_date2)
        self.assertEqual(
            instance2.date - instance1.date, original_date2 - original_date1
        )

    def test_string_is_properly_anonymized(self):
        original_identifier = "123456789"
        instance = self.TestGetSchema(
            id=uuid4(),
            description="test",
            identifier=original_identifier,
            anonymized=True,
        )
        self.assertNotEqual(instance.identifier, original_identifier)
        self.assertEqual(instance.identifier, REDACTED_STRING)

    def test_string_can_be_deanonymized(self):
        original_identifier = "123456789"
        instance = self.TestGetSchema(
            id=uuid4(),
            description="test",
            identifier=original_identifier,
            anonymized=False,
        )
        self.assertEqual(instance.identifier, original_identifier)
        self.assertEqual(instance.identifier, original_identifier)
