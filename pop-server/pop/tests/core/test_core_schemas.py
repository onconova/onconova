
from typing import Optional, List
from uuid import UUID
from pydantic_core import PydanticUndefined

from django.test import TestCase, TransactionTestCase
from django.db import models as django_models
from django.db.models import CharField, ForeignKey, ManyToManyField, TextChoices

from pop.oncology.models import PatientCase
from pop.terminology.models import CodedConcept as CodedConceptBase, AdministrativeGender
from pop.core.schemas.fields import get_schema_field, CodedConceptSchema, get_schema_field, PydanticUndefined
from pop.core.schemas.factory import SchemaFactory
from pop.core.schemas import CodedConceptSchema
from pop.tests.factories import UserFactory, PatientCaseFactory



class TestGetSchemaField(TestCase):

    def setUp(self):
        self.MockModel = PatientCase
        self.MockCodedConcept = AdministrativeGender
    
    def _create_foreign_key_field(self, model, null=False):
        field = ForeignKey(model, on_delete=django_models.CASCADE, name='test_field', null=null)
        field.is_relation = True
        field.related_model = model
        field.concrete = False
        return field
    
    def _assert_naming_and_aliases(self, schema_field_name, field_info, expected_name, expected_alias):
        self.assertEqual(schema_field_name, expected_name)
        self.assertEqual(field_info.alias, expected_alias)
        self.assertEqual(field_info.validation_alias.choices, [expected_name, expected_alias])
        self.assertEqual(field_info.serialization_alias, expected_name)

    def test_non_relation_field_with_default_value(self):
        field = CharField(max_length=255, default='test_default', name='test_field')
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testField', 'test_field')
        self.assertEqual(python_type, str)
        self.assertEqual(field_info.default, 'test_default')

    def test_non_relation_field_without_default_value(self):
        field = CharField(max_length=255, name='test_field')
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testField', 'test_field')
        self.assertEqual(python_type, str)
        self.assertEqual(field_info.default, PydanticUndefined)

    def test_charfield_with_choices(self):
        choices = [('a', 'optionA'),('b', 'optionB')]
        field = CharField(max_length=255, name='test_field', choices=choices)
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testField', 'test_field')
        self.assertEqual([e.value for e in python_type], [choice[0] for choice in choices])
        self.assertEqual(field_info.default, PydanticUndefined)
        
    def test_relation_field_with_expand_true(self):
        field = self._create_foreign_key_field(model=self.MockModel)
        schema_field_name, (python_type, field_info) = get_schema_field(field, expand='MockModel')
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testField', 'test_field')
        self.assertIsInstance(python_type, type)
        self.assertEqual(field_info.default, PydanticUndefined)

    def test_relation_field_with_expand_false(self):
        field = self._create_foreign_key_field(model=self.MockModel)
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testFieldId', 'test_field_id')
        self.assertEqual(python_type, UUID)
        self.assertEqual(field_info.default, PydanticUndefined)

    def test_relation_field_with_optional_true(self):
        field = self._create_foreign_key_field(model=self.MockModel)
        schema_field_name, (python_type, field_info) = get_schema_field(field, optional=True)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testFieldId', 'test_field_id')
        self.assertEqual(python_type, Optional[UUID])
        self.assertEqual(field_info.default, None)

    def test_relation_field_with_nullable_true(self):
        field = self._create_foreign_key_field(model=self.MockModel, null=True)
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testFieldId', 'test_field_id')
        self.assertEqual(python_type, Optional[UUID])
        self.assertEqual(field_info.default, None)

    def test_coded_concept_field(self):
        field = self._create_foreign_key_field(model=self.MockCodedConcept)
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testField', 'test_field')
        self.assertEqual(python_type, CodedConceptSchema)
        self.assertEqual(field_info.default, PydanticUndefined)

    def test_many_to_many_field(self):
        field = ManyToManyField(self.MockModel, name='test_fields')
        field.is_relation = True
        field.related_model = self.MockModel
        field.concrete = False
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testFieldsIds', 'test_fields_ids')
        self.assertEqual(python_type, List[UUID])
        self.assertEqual(field_info.default, [])

