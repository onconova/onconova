from django.db import connection
from django.db.models.base import ModelBase
from django.test import TestCase

class AbstractModelMixinTestCase(TestCase):
    """
    Abstract test case for mixin class.
    """

    mixin = None
    model = None

    @classmethod
    def setUpClass(cls) -> None:
        """Create a test model from the mixin"""
        class Meta:
            """Meta options for the temporary model"""
            app_label = 'test'
        cls.model = ModelBase(
            "Test" + cls.mixin.__name__,
            (cls.mixin,),
            {
                "__module__": cls.mixin.__module__,
                "Meta":Meta,
            }
        )

        with connection.schema_editor() as editor:
            editor.create_model(cls.model)

        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        """Delete the test model"""
        super().tearDownClass()

        with connection.schema_editor() as editor:
            editor.delete_model(cls.model)

        connection.close()
