from datetime import date
from unittest import TestCase
from unittest.mock import MagicMock, patch

from django.contrib.postgres.fields import (
    BigIntegerRangeField,
    DateRangeField,
    IntegerRangeField,
)
from django.db import models
from pydantic_core import PydanticUndefined  # type: ignore

from pop.core.measures import Measure
from pop.core.measures.fields import MeasurementField
from pop.core.models import User
from pop.core.schemas import CodedConcept as CodedConceptSchema
from pop.core.schemas import Period as PeriodSchema
from pop.core.schemas import Range as RangeSchema
from pop.core.serialization.fields import (
    DJANGO_TO_PYDANTIC_TYPES,
    SchemaFieldInfo,
    get_related_field_type,
    process_non_relation_field,
)
from pop.core.types import Username
from pop.tests.models import MockCodedConcept


class DummyMeasurement:
    __name__ = "DummyUnit"


class DummyModel(models.Model):
    class Meta:
        app_label = "test"


class TestProcessNonRelationField(TestCase):

    def test_measurement_field(self):
        field = MagicMock(spec=MeasurementField)
        field.name = "weight"
        field.get_internal_type.return_value = "FloatField"
        field.measurement = DummyMeasurement
        field.get_default_unit.return_value = "mg__dl"
        field.has_default.return_value = False
        field.primary_key = False

        info = process_non_relation_field(field)
        self.assertIsInstance(info, SchemaFieldInfo)
        self.assertEqual(info.python_type, Measure)
        self.assertEqual(info.extras["x-measure"], "DummyMeasurement")
        self.assertEqual(info.extras["x-default-unit"], "mg/dl")
        self.assertTrue(callable(info.resolver_fcn))

    def test_date_range_field(self):
        field = DateRangeField()
        field.name = "period"
        field.get_internal_type = lambda: "DateRangeField"
        field.has_default = lambda: False
        field.primary_key = False

        info = process_non_relation_field(field)
        self.assertIsInstance(info, SchemaFieldInfo)
        self.assertEqual(info.python_type, PeriodSchema)
        self.assertIsNone(info.resolver_fcn)

    def test_integer_range_field(self):
        field = IntegerRangeField()
        field.name = "range"
        field.get_internal_type = lambda: "IntegerRangeField"
        field.has_default = lambda: False
        field.primary_key = False

        info = process_non_relation_field(field)
        self.assertIsInstance(info, SchemaFieldInfo)
        self.assertEqual(info.python_type, RangeSchema)
        self.assertIsNone(info.resolver_fcn)

    def test_big_integer_range_field(self):
        field = BigIntegerRangeField()
        field.name = "range"
        field.get_internal_type = lambda: "BigIntegerRangeField"
        field.has_default = lambda: False
        field.primary_key = False

        info = process_non_relation_field(field)
        self.assertIsInstance(info, SchemaFieldInfo)
        self.assertEqual(info.python_type, RangeSchema)
        self.assertIsNone(info.resolver_fcn)

    def test_charfield_with_choices_enum(self):
        class DummyEnumModel(models.Model):
            STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]
            status = models.CharField(max_length=10, choices=STATUS_CHOICES)

            class Meta:
                app_label = "test"

        field = DummyEnumModel._meta.get_field("status")
        field.has_default = lambda: False
        field.primary_key = False

        info = process_non_relation_field(field)
        self.assertIsInstance(info, SchemaFieldInfo)
        self.assertTrue(issubclass(info.python_type, str))
        self.assertTrue(hasattr(info.python_type, "__members__"))
        self.assertIn("ACTIVE", info.python_type.__members__)
        self.assertIn("INACTIVE", info.python_type.__members__)

    def test_fallback_to_str(self):
        field = models.CharField(max_length=20)
        field.name = "plain"
        field.get_internal_type = lambda: "CharField"
        field.has_default = lambda: False
        field.primary_key = False

        info = process_non_relation_field(field)
        self.assertIsInstance(info, SchemaFieldInfo)
        self.assertEqual(info.python_type, str)

    def test_default_and_default_factory(self):
        field = models.CharField(max_length=20, default="abc")
        field.name = "plain"
        field.get_internal_type = lambda: "CharField"
        field.has_default = lambda: True
        field.primary_key = False
        field.default = "abc"

        info = process_non_relation_field(field)
        self.assertEqual(info.default, "abc")
        self.assertIsNone(info.default_factory)

    def test_default_factory_callable(self):
        field = models.DateField(default=date.today)
        field.name = "created"
        field.get_internal_type = lambda: "DateField"
        field.has_default = lambda: True
        field.primary_key = False
        field.default = date.today

        info = process_non_relation_field(field)
        self.assertEqual(PydanticUndefined, info.default)
        self.assertTrue(callable(info.default_factory))
        field.primary_key = False
        field.default = date.today


class DummyRelatedModel(models.Model):
    class Meta:
        app_label = "test"


class DummyForeignKey(models.ForeignKey):
    def __init__(self, to, **kwargs):
        super().__init__(to, **kwargs)
        self.name = "dummy"
        self.many_to_many = False
        self.related_model = to
        self.many_to_one = True
        self.one_to_many = False
        self.auto_created = False
        self.null = False
        self.blank = False


class DummyManyToManyField(models.ManyToManyField):
    def __init__(self, to, **kwargs):
        super().__init__(to, **kwargs)
        self.name = "dummy"
        self.many_to_many = True
        self.related_model = to
        self.many_to_one = False
        self.one_to_many = False
        self.auto_created = False
        self.null = False
        self.blank = False


class DummyField(MagicMock):
    def __init__(self, related_model, many_to_many=False):
        self.name = "dummy"
        self.related_model = related_model
        self.many_to_many = many_to_many
        self.many_to_one = not many_to_many
        self.one_to_many = False
        self.auto_created = False
        self.null = False
        self.blank = False

    def __getattr__(self, item):
        # fallback for missing attributes
        return False


class TestGetRelatedFieldType(TestCase):
    def test_coded_concept_model(self):
        field = DummyField(MockCodedConcept)
        resolver, typ, alias, extras = get_related_field_type(
            field, MockCodedConcept, "dummy"
        )
        self.assertIsNone(resolver)
        self.assertIs(typ, CodedConceptSchema)
        self.assertEqual(alias, "dummy")
        self.assertIn("x-terminology", extras)
        self.assertEqual(extras["x-terminology"], "MockCodedConcept")

    def test_user_model(self):
        field = DummyField(User)
        resolver, typ, alias, extras = get_related_field_type(field, User, "dummy")
        self.assertTrue(callable(resolver))
        self.assertEqual(alias, "dummy")
        self.assertEqual(extras, {})

    def test_many_to_many(self):
        related_model = DummyRelatedModel
        # Patch _meta.get_field("id").get_internal_type to return "AutoField"
        related_model._meta.get_field = MagicMock(
            return_value=MagicMock(get_internal_type=lambda: "AutoField")
        )
        field = DummyField(related_model, many_to_many=True)
        resolver, typ, alias, extras = get_related_field_type(
            field, related_model, "dummy"
        )
        self.assertTrue(callable(resolver))
        self.assertEqual(typ, DJANGO_TO_PYDANTIC_TYPES.get("AutoField", int))
        self.assertEqual(alias, "dummyIds")
        self.assertEqual(extras, {})

    def test_foreign_key(self):
        related_model = DummyRelatedModel
        related_model._meta.get_field = MagicMock(
            return_value=MagicMock(get_internal_type=lambda: "BigAutoField")
        )
        field = DummyField(related_model, many_to_many=False)
        resolver, typ, alias, extras = get_related_field_type(
            field, related_model, "dummy"
        )
        self.assertTrue(callable(resolver))
        self.assertEqual(typ, DJANGO_TO_PYDANTIC_TYPES.get("BigAutoField", int))
        self.assertEqual(alias, "dummyId")
        self.assertEqual(extras, {})
        related_model = DummyRelatedModel
        related_model._meta.get_field = MagicMock(
            return_value=MagicMock(get_internal_type=lambda: "BigAutoField")
        )
        field = DummyField(related_model, many_to_many=False)
        resolver, typ, alias, extras = get_related_field_type(
            field, related_model, "dummy"
        )
        self.assertTrue(callable(resolver))
        self.assertEqual(typ, DJANGO_TO_PYDANTIC_TYPES.get("BigAutoField", int))
        self.assertEqual(alias, "dummyId")
        self.assertEqual(extras, {})
