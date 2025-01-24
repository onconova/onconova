import warnings
from typing import Any, List, Dict, Optional, Union, no_type_check

from django.db.models import Model as DjangoModel 

from ninja.schema import ResolverMetaclass
from ninja.errors import ConfigError
from pydantic.dataclasses import dataclass

from pop.core.schemas.factory import create_schema, create_filters_schema
from pop.core.schemas.base import BaseSchema 

_is_modelschema_class_defined = False

@dataclass
class MetaConf:
    model: Any
    fields: Optional[List[str]] = None
    exclude: Union[List[str], str, None] = None
    schema_name: str = None
    expand: Optional[Dict] = None
    reverse_fields: Optional[List[str]] = None
    fields_optional: Union[List[str], str, None] = None

    @staticmethod
    def from_schema_class(name: str, namespace: dict) -> "MetaConf":
        if "Meta" in namespace:
            meta = namespace["Meta"]
            model = meta.model
            fields = getattr(meta, "fields", None)
            reverse_fields = getattr(meta, "reverse_fields", None)
            expand = getattr(meta, "expand", None)
            schema_name = getattr(meta, "name", name)
            exclude = getattr(meta, "exclude", None)
            optional_fields = getattr(meta, "fields_optional", None)
        else:
            raise ConfigError(
                f"ModelSchema class '{name}' requires a 'Meta' subclass"
            )

        assert issubclass(model, DjangoModel)

        if not fields and not exclude:
            raise ConfigError(
                "Creating a ModelSchema without either the 'fields' attribute"
                " or the 'exclude' attribute is prohibited"
            )

        if fields == "__all__":
            fields = None
            # ^ when None is passed to create_schema - all fields are selected

        return MetaConf(
            model=model,
            fields=fields,
            reverse_fields=reverse_fields,
            schema_name=schema_name,
            exclude=exclude,
            expand=expand,
            fields_optional=optional_fields,
        )

class ModelSchemaMetaclass(ResolverMetaclass):
    @no_type_check
    def __new__(
        mcs,
        name: str,
        bases: tuple,
        namespace: dict,
        **kwargs,
    ):
        cls = super().__new__(
            mcs,
            name,
            bases,
            namespace,
            **kwargs,
        )
        for base in reversed(bases):
            if (
                _is_modelschema_class_defined
                and issubclass(base, ModelSchema)
                and base == ModelSchema
            ):
                meta_conf = MetaConf.from_schema_class(name, namespace)

                custom_fields = []
                annotations = namespace.get("__annotations__", {})
                for attr_name, type in annotations.items():
                    if attr_name.startswith("_"):
                        continue
                    default = namespace.get(attr_name, ...)
                    custom_fields.append((attr_name, type, default))

                # # cls.__doc__ = namespace.get("__doc__", config.model.__doc__)
                # cls.__fields__ = {}  # forcing pydantic recreate
                # # assert False, "!! cls.model_fields"

                # print(config.model, name, fields, exclude, "!!")

                model_schema = create_schema(
                    meta_conf.model,
                    name=meta_conf.schema_name,
                    fields=meta_conf.fields,
                    exclude=meta_conf.exclude,
                    expand=meta_conf.expand,
                    reverse_fields=meta_conf.reverse_fields,
                    optional_fields=meta_conf.fields_optional,
                    custom_fields=custom_fields,
                    base_class=cls,
                )
                model_schema.__doc__ = cls.__doc__
                return model_schema

        return cls



class ModelSchema(BaseSchema, metaclass=ModelSchemaMetaclass):
    pass

class ModelFilterSchema(BaseSchema):

    @classmethod
    def get_django_lookup(cls, filter_name):
        filter_info = cls.model_fields.get(filter_name)
        return filter_info.json_schema_extra.get('django_lookup')


_is_modelschema_class_defined = True
