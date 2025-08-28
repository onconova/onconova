from datetime import datetime, timedelta
from uuid import UUID, uuid4

from onconova.core.models import BaseModel
from onconova.tests.common import AbstractModelMixinTestCase
from onconova.tests.models import MockBaseModel


class BaseModelTestCase(AbstractModelMixinTestCase):
    mixin = BaseModel

    def test_init_with_id(self):
        id = uuid4()
        obj = self.model(id=id)
        self.assertEqual(obj.id, id)

    def test_init_without_id(self):
        obj = self.model()
        self.assertIsInstance(obj.id, UUID)

    def test_description_not_implemented(self):
        obj = self.model()
        with self.assertRaises(NotImplementedError):
            obj.description

    def test_created_at_annotation(self):
        before_create = datetime.now() - timedelta(minutes=1)
        obj = MockBaseModel.objects.create(id=uuid4())
        self.assertIsNotNone(obj.created_at)
        self.assertGreater(obj.created_at, before_create)  # type: ignore
        self.assertIsNone(obj.updated_at)

    def test_updated_at_annotation(self):
        obj = MockBaseModel.objects.create(id=uuid4())
        obj.external_source = "test"
        obj.save()
        self.assertGreaterEqual(obj.updated_at, obj.created_at)  # type: ignore

    def test_base_model_inherits_fields(self):
        obj = self.model()
        assert obj.id is not None
        assert obj.external_source is None
        assert obj.external_source_id is None
