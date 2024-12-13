
from typing import Optional, List

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
    
    def _assert_django_field_properties(self, django_field, field_info):
        print(field_info.json_schema_extra)
        self.assertEqual(field_info.json_schema_extra.get('orm_name'), django_field.name)
        self.assertEqual(field_info.json_schema_extra.get('many_to_many'), bool(django_field.many_to_many))
        self.assertEqual(field_info.json_schema_extra.get('one_to_many'), bool(django_field.one_to_many))
        self.assertEqual(field_info.json_schema_extra.get('is_relation'), bool(django_field.is_relation))

    def _assert_naming_and_aliases(self, schema_field_name, field_info, expected_name, expected_alias):
        self.assertEqual(schema_field_name, expected_name)
        self.assertEqual(field_info.alias, expected_alias)
        self.assertEqual(field_info.validation_alias.choices, [expected_name, expected_alias])
        self.assertEqual(field_info.serialization_alias, expected_name)

    def test_non_relation_field_with_default_value(self):
        field = CharField(max_length=255, default='test_default', name='test_field')
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testField', 'test_field')
        self._assert_django_field_properties(field, field_info)
        self.assertEqual(python_type, str)
        self.assertEqual(field_info.default, 'test_default')

    def test_non_relation_field_without_default_value(self):
        field = CharField(max_length=255, name='test_field')
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testField', 'test_field')
        self._assert_django_field_properties(field, field_info)
        self.assertEqual(python_type, str)
        self.assertEqual(field_info.default, PydanticUndefined)

    def test_charfield_with_choices(self):
        choices = [('a', 'optionA'),('b', 'optionB')]
        field = CharField(max_length=255, name='test_field', choices=choices)
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testField', 'test_field')
        self._assert_django_field_properties(field, field_info)
        self.assertEqual([e.value for e in python_type], [choice[0] for choice in choices])
        self.assertEqual(field_info.default, PydanticUndefined)
        
    def test_relation_field_with_expand_true(self):
        field = self._create_foreign_key_field(model=self.MockModel)
        schema_field_name, (python_type, field_info) = get_schema_field(field, expand=True)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testField', 'test_field')
        self._assert_django_field_properties(field, field_info)
        self.assertIsInstance(python_type, type)
        self.assertEqual(field_info.default, PydanticUndefined)

    def test_relation_field_with_expand_false(self):
        field = self._create_foreign_key_field(model=self.MockModel)
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testFieldId', 'test_field_id')
        self.assertEqual(python_type, str)
        self.assertEqual(field_info.default, PydanticUndefined)

    def test_relation_field_with_optional_true(self):
        field = self._create_foreign_key_field(model=self.MockModel)
        schema_field_name, (python_type, field_info) = get_schema_field(field, optional=True)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testFieldId', 'test_field_id')
        self._assert_django_field_properties(field, field_info)
        self.assertEqual(python_type, Optional[str])
        self.assertEqual(field_info.default, None)

    def test_relation_field_with_nullable_true(self):
        field = self._create_foreign_key_field(model=self.MockModel, null=True)
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testFieldId', 'test_field_id')
        self._assert_django_field_properties(field, field_info)
        self.assertEqual(python_type, Optional[str])
        self.assertEqual(field_info.default, None)

    def test_coded_concept_field(self):
        field = self._create_foreign_key_field(model=self.MockCodedConcept)
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testField', 'test_field')
        self._assert_django_field_properties(field, field_info)
        self.assertEqual(python_type, CodedConceptSchema)
        self.assertEqual(field_info.default, PydanticUndefined)

    def test_many_to_many_field(self):
        field = ManyToManyField(self.MockModel, name='test_fields')
        field.is_relation = True
        field.related_model = self.MockModel
        field.concrete = False
        schema_field_name, (python_type, field_info) = get_schema_field(field)
        self._assert_naming_and_aliases(schema_field_name, field_info, 'testFieldsIds', 'test_fields_ids')
        self._assert_django_field_properties(field, field_info)
        self.assertEqual(python_type, List[str])
        self.assertEqual(field_info.default, [])



class TestSchemaFactory(TestCase):

    def setUp(self):
        self.factory = SchemaFactory()

    def test_creating_schema_with_nonrelational_field(self):
        django_instance = PatientCaseFactory()
        # Create schema
        schema = self.factory.create_schema(PatientCase, exclude=['id', 'pseudoidentifier'])
        schema_instance = schema.model_validate(django_instance)
        # Assertion
        self.assertEqual(schema_instance.createdAt, django_instance.created_at)
        self.assertEqual(schema_instance.model_dump()['createdAt'],  django_instance.created_at)
        self.assertEqual(schema_instance.model_dump_django().created_at.day, django_instance.created_at.day)

    def test_creating_schema_with_relational_field(self):
        user = UserFactory()
        django_instance = PatientCaseFactory(created_by=user)
        # Create schema
        schema = self.factory.create_schema(PatientCase)
        schema_instance = schema.model_validate(django_instance)
        # Assertion
        django_instance.user = None;
        django_instance.save()
        self.assertEqual(schema_instance.createdById, user.id)
        self.assertEqual(schema_instance.model_dump()['createdById'], user.id)
        self.assertEqual(schema_instance.model_dump_django(instance=django_instance).created_by, user)

    def test_creating_schema_with_nullable_relational_field(self):
        user = UserFactory()
        django_instance = PatientCaseFactory(created_by=user)
        # Create schema
        schema = self.factory.create_schema(PatientCase)
        schema_instance = schema.model_validate(django_instance)
        schema_instance.race = None
        # Assertion
        self.assertIsNotNone(django_instance.race)
        self.assertIsNone(schema_instance.model_dump_django(instance=django_instance).race)
        
    def test_creating_schema_with_codedconcept_field(self):
        django_instance = PatientCaseFactory()
        related_concept = django_instance.gender 
        # Create schema
        schema = self.factory.create_schema(PatientCase)
        schema_instance = schema.model_validate(django_instance)
        # Assertion
        django_instance.gender = None;
        self.assertEqual(schema_instance.gender.model_dump(), CodedConceptSchema.model_validate(related_concept).model_dump())
        self.assertEqual(schema_instance.model_dump_django(instance=django_instance).gender, related_concept)

    def test_creating_schema_with_manytomany_field(self):
        user1 = UserFactory()
        user2 = UserFactory()
        django_instance = PatientCaseFactory()
        django_instance.updated_by.add(user1)
        django_instance.updated_by.add(user2)

        # Create schema
        schema = self.factory.create_schema(PatientCase)
        schema_instance = schema.model_validate(django_instance)
        # Assertion
        django_instance.updated_by.set([])
        self.assertEqual(schema_instance.updatedByIds, [user1.id, user2.id])
        self.assertEqual(schema_instance.model_dump()['updatedByIds'],  [user1.id, user2.id])
        self.assertEqual(schema_instance.model_dump_django(instance=django_instance).updated_by.first(), user1)
        self.assertEqual(schema_instance.model_dump_django(instance=django_instance).updated_by.last(), user2)


    def test_creating_schema_with_expanded_manytomany_field(self):
        user1 = UserFactory()
        user2 = UserFactory()
        django_instance = PatientCaseFactory()
        django_instance.updated_by.add(user1)
        django_instance.updated_by.add(user2)

        # Create schema
        schema = self.factory.create_schema(PatientCase, expand=['updated_by'])
        schema_instance = schema.model_validate(django_instance)
        # Assertion
        django_instance.updated_by.set([])
        self.assertEqual([user['username'] for user in schema_instance.model_dump()['updatedBy']],  [user1.username, user2.username])
        self.assertEqual(schema_instance.model_dump_django(instance=django_instance).updated_by.first(), user1)
        self.assertEqual(schema_instance.model_dump_django(instance=django_instance).updated_by.last(), user2)
        

        