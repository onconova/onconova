
import json 
from typing import Optional

from unittest import TestCase
from unittest.mock import MagicMock

from parameterized import parameterized

from pydantic_core import PydanticUndefined

from django.db import models as django_models
from django.contrib.auth.models import User

from pop.terminology.models import AdministrativeGender as MockCodedConcept
from pop.oncology.schemas.fields import get_schema_field, CodedConcept as CodedConceptSchema
from pop.oncology.schemas.factory import SchemaFactory
from pop.tests.factories import UserFactory, make_terminology_factory

class TestGetSchemaField(TestCase):

    def test_getting_a_codedconcept_field(self):
        # Create a relation field
        field = django_models.ForeignKey('self', on_delete=django_models.CASCADE)
        field.is_relation = True
        field.related_model = MockCodedConcept
        field.concrete = False
        field.name = 'test_field'

        # Test get_schema_field
        field_name, (python_type, field_info) = get_schema_field(field)
        self.assertEqual(python_type, CodedConceptSchema)
        self.assertEqual(field_info.default, PydanticUndefined)
        self.assertEqual(field_name, 'test_field')
        self.assertEqual(field_info.alias, 'testField')

    def test_getting_a_relation_field(self):
        # Create a relation field
        field = django_models.ForeignKey('self', on_delete=django_models.CASCADE)
        field.is_relation = True
        field.related_model = User
        field.concrete = False
        field.name = 'test_field'

        # Test get_schema_field
        field_name, (python_type, field_info) = get_schema_field(field)
        self.assertEqual(python_type, int)
        self.assertEqual(field_info.default, PydanticUndefined)
        self.assertEqual(field_name, 'test_field_id')
        self.assertEqual(field_info.alias, 'testFieldId')

    def test_getting_a_non_relation_field(self):
        # Create a non-relation field
        field = django_models.CharField(max_length=255)
        field.is_relation = False
        field.name = 'test_field'

        # Test get_schema_field
        field_name, (python_type, field_info) = get_schema_field(field)
        self.assertEqual(python_type, str)
        self.assertEqual(field_info.default, PydanticUndefined)
        self.assertEqual(field_name, 'test_field')
        self.assertEqual(field_info.alias, 'testField')

    def test_getting_a_relation_field_with_depth(self):
        # Create a relation field
        field = django_models.ForeignKey('self', on_delete=django_models.CASCADE)
        field.is_relation = True
        field.related_model = User
        field.concrete = False
        field.name = 'test_field'

        # Test get_schema_field with depth greater than 0
        field_name, (python_type, field_info) = get_schema_field(field, depth=1)
        self.assertNotEqual(python_type, int)
        self.assertEqual(field_info.default, PydanticUndefined)
        self.assertEqual(field_name, 'test_field')
        self.assertEqual(field_info.alias, 'testField')

    def test_getting_a_field_with_default_value(self):
        # Create a field with a default value
        field = django_models.CharField(max_length=255, default='test_default')
        field.is_relation = False
        field.name = 'test_field'

        # Test get_schema_field
        field_name, (python_type, field_info) = get_schema_field(field)
        self.assertEqual(python_type, str)
        self.assertEqual(field_info.default, 'test_default')
        self.assertEqual(field_name, 'test_field')
        self.assertEqual(field_info.alias, 'testField')

    def test_getting_an_optional_field(self):
        # Create an optional field
        field = django_models.CharField(max_length=255, blank=True, null=True)
        field.is_relation = False
        field.name = 'test_field'

        # Test get_schema_field
        field_name, (python_type, field_info) = get_schema_field(field, optional=True)
        self.assertEqual(python_type, Optional[str])
        self.assertEqual(field_info.default, None)
        self.assertEqual(field_name, 'test_field')
        self.assertEqual(field_info.alias, 'testField')

    def test_getting_a_nullable_field(self):
        # Create a nullable field
        field = django_models.CharField(max_length=255, null=True)
        field.is_relation = False
        field.name = 'test_field'

        # Test get_schema_field
        field_name, (python_type, field_info) = get_schema_field(field)
        self.assertEqual(python_type, Optional[str])
        self.assertEqual(field_info.default, None)
        self.assertEqual(field_name, 'test_field')
        self.assertEqual(field_info.alias, 'testField')


    def test_getting_a_many_to_many_field(self):
        # Create a many-to-many field
        field = django_models.ManyToManyField('self')
        field.is_relation = True
        field.related_model = User
        field.concrete = True
        field.name = 'test_field'

        # Test get_schema_field
        field_name, (python_type, field_info) = get_schema_field(field)
        self.assertEqual(field_info.default, [])
        self.assertEqual(field_name, 'test_field_id')
        self.assertEqual(field_info.alias, 'testFieldId')

class TestSchemaFactory(TestCase):

    def setUp(self):
        self.factory = SchemaFactory()

    def _setup_model(self, fields):
        model_meta = MagicMock()
        model_meta.get_fields.return_value = fields
        return MagicMock(
            __name__='MyModel', 
            _meta=model_meta
        )

    def test_create_schema_returns_schema_with_correct_name(self):
        # Setup model
        model = self._setup_model([])
        # Assertion
        schema = self.factory.create_schema(model)
        self.assertEqual(schema.__name__, 'MyModel')

    def test_creating_schema_with_nonrelational_field(self):
        # Setup model field
        field = django_models.CharField(max_length=255, null=True)
        field.is_relation = False
        field.name = 'test_field'
        # Setup model
        model = self._setup_model([field])
        # Create schema
        schema = self.factory.create_schema(model)
        # Instantiate
        input_value = 'test_value'
        expected_value = input_value
        instance = schema(test_field=input_value)
        # Assertion
        self.assertEqual(len(schema.model_fields), 1)
        self.assertEqual(instance.test_field, expected_value)
        self.assertEqual(instance.model_dump(), {'testField': expected_value})

    def test_creating_schema_with_relational_field(self):
        # Setup model field
        field = django_models.ForeignKey('self', on_delete=django_models.CASCADE)
        field.is_relation = True
        field.related_model = User
        field.concrete = False
        field.name = 'test_field'
        # Setup model
        model = self._setup_model([field])
        # Create schema
        schema = self.factory.create_schema(model)
        # Instantiate
        input_value = UserFactory().id
        expected_value = input_value
        instance = schema(test_field_id=input_value)
        # Assertion
        self.assertEqual(len(schema.model_fields), 1)
        self.assertEqual(instance.test_field_id, expected_value)
        self.assertEqual(instance.model_dump(), {'testFieldId': expected_value})

    def test_creating_schema_with_codedconcept_field(self):
        # Setup model field
        field = django_models.ForeignKey('self', on_delete=django_models.CASCADE)
        field.is_relation = True
        field.related_model = MockCodedConcept
        field.concrete = False
        field.name = 'test_field'
        # Setup model
        model = self._setup_model([field])
        # Create schema
        schema = self.factory.create_schema(model)
        # Instantiate
        concept = make_terminology_factory(MockCodedConcept).create()
        input_value = CodedConceptSchema.model_validate({
            'code': concept.code,
            'diplay': concept.display,
            'system': concept.system,
        })
        expected_value = input_value
        instance = schema.model_validate({'test_field': input_value})
        # Assertion
        self.assertEqual(len(schema.model_fields), 1)
        self.assertEqual(instance.test_field, expected_value)
