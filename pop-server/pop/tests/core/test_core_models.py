import random
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
        with patch('random.randint', side_effect=[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]):
            instance = self.model()
        self.assertEqual(instance.id, 'POP-TestBaseModel-123456789')

    def test_generate_unique_id(self):
        instance = self.model()
        with patch('random.randint', side_effect=[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]):
            new_id = instance._generate_unique_id()
        self.assertEqual(new_id, 'POP-TestBaseModel-123456789')

    def test_description_not_implemented(self):
        instance = self.model()
        with self.assertRaises(NotImplementedError):
            str(instance)
