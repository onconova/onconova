import inspect
import unittest

from parameterized import parameterized
from pydantic import BaseModel, Field

from onconova.analytics import schemas as analytics_schemas
from onconova.core import schemas as core_schemas
from onconova.oncology import schemas as oncology_schemas
from onconova.research import schemas as research_schemas


class TestSchemas(unittest.TestCase):

    @parameterized.expand(
        [
            core_schemas,
            oncology_schemas,
            research_schemas,
            analytics_schemas,
        ],
        name_func=lambda fcn, idx, param: f"{fcn.__name__}_{list(param)[0][0].__name__.split('.')[-2]}",
    )
    def test_all_schema_fields_have_title_and_description(self, module):

        # Find all Schema classes in the module
        schema_classes = [
            cls
            for name, cls in inspect.getmembers(module, inspect.isclass)
            if issubclass(cls, BaseModel)
            and "onconova" in cls.__module__
            and cls.__name__ not in ["Paginated"]
        ]
        self.assertTrue(schema_classes, "No Schema classes found in the module")

        for schema_cls in schema_classes:
            for field_name, field in schema_cls.model_fields.items():
                # Only check fields created with Field(...)
                title = getattr(field, "title", None)
                description = getattr(field, "description", None)
                self.assertIsNotNone(
                    title, f"{schema_cls.__name__}.{field_name} is missing title"
                )
                self.assertNotEqual(
                    title, "", f"{schema_cls.__name__}.{field_name} has empty title"
                )
                self.assertIsNotNone(
                    description,
                    f"{schema_cls.__name__}.{field_name} is missing description",
                )
                self.assertNotEqual(
                    description,
                    "",
                    f"{schema_cls.__name__}.{field_name} has empty description",
                )
                self.assertIsNotNone(
                    description,
                    f"{schema_cls.__name__}.{field_name} is missing description",
                )
                self.assertNotEqual(
                    description,
                    "",
                    f"{schema_cls.__name__}.{field_name} has empty description",
                )
