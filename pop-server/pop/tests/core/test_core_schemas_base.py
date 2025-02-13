import unittest
from django.db.models import Model, CharField, IntegerField
from pop.core.schemas.factory.base import OrmMetadataMixin

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