import unittest
from typing import Optional
from datetime import datetime
from uuid import uuid4
from pydantic import Field
from django.db.models import Model, CharField, IntegerField
from pop.core.anonymization import AnonymizationMixin, ANONYMIZED_STRING
from pop.core.schemas.factory.base import OrmMetadataMixin
from pop.core.schemas.factory.metaclasses import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.tests.models import UntrackedMockBaseModel

class TestOrmMetadataMixin(unittest.TestCase):

    def test_set_single_valid_metadata(self):
        class TestClass(OrmMetadataMixin):
            pass
        field = CharField()
        TestClass.set_orm_metadata(field1=field)
        self.assertEqual(TestClass.__orm_meta__, {'field1': field})

    def test_set_multiple_valid_metadata(self):
        class TestClass(OrmMetadataMixin):
            pass
        field1 = CharField()
        field2 = IntegerField()
        TestClass.set_orm_metadata(field1=field1, field2=field2)
        self.assertEqual(TestClass.__orm_meta__, {'field1': field1, 'field2': field2})

    def test_set_invalid_metadata_non_django_field(self):
        class TestClass(OrmMetadataMixin):
            pass
        with self.assertRaises(TypeError):
            TestClass.set_orm_metadata(field1='not a DjangoField')

    def test_set_invalid_metadata_as_type(self):
        class TestClass(OrmMetadataMixin):
            pass
        with self.assertRaises(TypeError):
            TestClass.set_orm_metadata(field1=CharField)  # Note: CharField is a type, but we're passing an instance

    def test_set_valid_orm_model(self):
        class TestClass(OrmMetadataMixin):
            pass
        model = Model
        TestClass.set_orm_model(model)
        self.assertEqual(TestClass.get_orm_model(), model)

    def test_set_multiple_subclasses(self):
        class TestClassA(OrmMetadataMixin):
            pass
        class TestClassB(OrmMetadataMixin):
            pass
        field1 = CharField()
        field2 = IntegerField()
        TestClassA.set_orm_metadata(field1=field1)
        TestClassB.set_orm_metadata(field2=field2)
        self.assertEqual(TestClassA.__orm_meta__, {'field1': field1})
        self.assertEqual(TestClassB.__orm_meta__, {'field2': field2})

    def test_set_none_orm_model(self):
        class TestClass(OrmMetadataMixin):
            pass
        TestClass.set_orm_model(None)
        self.assertIsNone(TestClass.get_orm_model())

    def test_set_non_model_orm_model(self):
        class TestClass(OrmMetadataMixin):
            pass
        non_model_object = "not a model"
        with self.assertRaises(TypeError):
            TestClass.set_orm_model(non_model_object)

    def test_get_orm_model_returns_set_model(self):
        class TestClass(OrmMetadataMixin):
            pass
        model = Model
        TestClass.set_orm_model(model)
        self.assertEqual(TestClass.get_orm_model(), model)

    def test_get_orm_model_returns_none_when_not_set(self):
        class TestClass(OrmMetadataMixin):
            pass
        self.assertIsNone(TestClass.get_orm_model())


    
class TestSchemaAnonymization(unittest.TestCase):

    class TestCreateSchema(ModelCreateSchema):
        config = SchemaConfig(model=UntrackedMockBaseModel)

    class TestGetSchema(ModelGetSchema, AnonymizationMixin):
        identifier: Optional[str] = Field(default=None)
        date: Optional[datetime] = Field(default=None)
        caseId: str = Field(default='test')
        config = SchemaConfig(model=UntrackedMockBaseModel, anonymization=dict(fields=('date','identifier'), key='caseId'))

    def test_create_model_schema_has_not_anonymized_field(self):
        instance = self.TestCreateSchema(id=uuid4(), description='test')
        self.assertFalse(hasattr(instance, 'anonymized'))
        
    def test_get_model_schema_has_anonymized_field(self):
        instance = self.TestGetSchema(id=uuid4(), description='test')
        self.assertTrue(hasattr(instance, 'anonymized'))
        
    def test_get_model_schema_is_not_anonymized_by_default(self):
        instance = self.TestGetSchema(id=uuid4(), description='test')
        self.assertFalse(instance.anonymized)

    def test_date_is_properly_anonymized(self):
        original_date = datetime(2000,1,1)
        instance = self.TestGetSchema(id=uuid4(), description='test', date=original_date, anonymized=True)
        self.assertNotEqual(instance.date, original_date)

    def test_date_can_be_deanonymized(self):
        original_date = datetime(2000,1,1)
        instance = self.TestGetSchema(id=uuid4(), description='test', date=original_date, anonymized=False)
        self.assertEqual(instance.date, original_date)
        
    def test_relative_dates_are_preserved_when_anonymized(self):
        original_date1 = datetime(2000,1,1)
        original_date2 = datetime(2000,2,2)
        instance1 = self.TestGetSchema(id=uuid4(), description='test', date=original_date1, anonymized=True)
        instance2 = self.TestGetSchema(id=uuid4(), description='test', date=original_date2, anonymized=True)
        self.assertNotEqual(instance1.date, original_date1)
        self.assertNotEqual(instance2.date, original_date2)
        self.assertEqual(instance2.date - instance1.date, original_date2 - original_date1)

    def test_string_is_properly_anonymized(self):
        original_identifier = '123456789'
        instance = self.TestGetSchema(id=uuid4(), description='test', identifier=original_identifier, anonymized=True)
        self.assertNotEqual(instance.identifier, original_identifier)
        self.assertEqual(instance.identifier, ANONYMIZED_STRING)
        
    def test_string_can_be_deanonymized(self):
        original_identifier = '123456789'
        instance = self.TestGetSchema(id=uuid4(), description='test', identifier=original_identifier, anonymized=False)
        self.assertEqual(instance.identifier, original_identifier)