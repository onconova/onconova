from uuid import UUID
from unittest import TestCase
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import connection

from pop.core.models import BaseModel
from pop.tests.common import AbstractModelMixinTestCase


class BaseModelTestCase(AbstractModelMixinTestCase):
    mixin = BaseModel

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_init_with_id(self):
        instance = self.model(id='test123')
        self.assertEqual(instance.id, 'test123')

    def test_init_without_id(self):
        instance = self.model()
        self.assertIsInstance(instance.id, UUID)

    def test_description_not_implemented(self):
        instance = self.model()
        with self.assertRaises(NotImplementedError):
            str(instance)
