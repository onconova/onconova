from datetime import datetime, timedelta
from uuid import UUID, uuid4
from pop.core.models import BaseModel
from pop.tests.models import MockBaseModel
from pop.tests.common import AbstractModelMixinTestCase

class BaseModelTestCase(AbstractModelMixinTestCase):
    mixin = BaseModel

    def test_init_with_id(self):
        id = uuid4()
        instance = self.model(id=id)
        self.assertEqual(instance.id, id)

    def test_init_without_id(self):
        instance = self.model()
        self.assertIsInstance(instance.id, UUID)

    def test_description_not_implemented(self):
        instance = self.model()
        with self.assertRaises(NotImplementedError):
            str(instance)

    def test_created_at_annotation(self):
        before_create = datetime.now()  - timedelta(minutes=1)
        instance = MockBaseModel.objects.create(id=uuid4())
        self.assertGreater(instance.created_at, before_create)
        self.assertIsNone(instance.updated_at)
        
    def test_updated_at_annotation(self):
        instance = MockBaseModel.objects.create(id=uuid4())
        instance.external_source = 'test'
        instance.save()
        self.assertGreaterEqual(instance.updated_at, instance.created_at)


