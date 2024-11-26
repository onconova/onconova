import warnings
from typing import Any, List, Optional, Union, no_type_check


from ninja.orm.metaclass import MetaConf
from ninja.schema import ResolverMetaclass, Schema

from pop.core.schemas.factory import create_schema
from pop.core.schemas.base import BaseSchema 

_is_modelschema_class_defined = False


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
                    name=name,
                    fields=meta_conf.fields,
                    exclude=meta_conf.exclude,
                    optional_fields=meta_conf.fields_optional,
                    custom_fields=custom_fields,
                    base_class=cls,
                )
                model_schema.__doc__ = cls.__doc__
                return model_schema

        return cls


class ModelSchema(BaseSchema, metaclass=ModelSchemaMetaclass):
    pass


_is_modelschema_class_defined = True