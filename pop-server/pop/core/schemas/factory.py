import itertools
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Type, Union, cast

from django.db.models import Field as DjangoField
from django.db.models import ManyToManyRel, ManyToOneRel, Model
from pydantic import field_validator, create_model as create_pydantic_model, ConfigDict, model_validator

from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar, Union, no_type_check

from ninja.errors import ConfigError
from ninja.orm.factory import SchemaFactory as NinjaSchemaFactory
from ninja.schema import Schema

from functools import partial 

from pop.core.schemas.fields import get_schema_field, CodedConcept

__all__ = ["SchemaFactory", "factory", "create_schema"]

SchemaKey = Tuple[Type[Model], str, int, str, str, str, str]

def to_camel_toe(string):
    return ''.join([
        word if n==0 else word.capitalize() 
            for n,word in enumerate(string.split('_'))
    ])

class SchemaFactory(NinjaSchemaFactory):
    
    IGNORE_FIELDS = ['auto_id']
    
    def create_schema(
        self,
        model: Type[Model],
        *,
        name: str = "",
        depth: int = 0,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        optional_fields: Optional[List[str]] = None,
        custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
        base_class: Type[Schema] = Schema,
    ) -> Type[Schema]:
        name = name or model.__name__

        if fields and exclude:
            raise ConfigError("Only one of 'fields' or 'exclude' should be set.")

        key = self.get_key(
            model, name, depth, fields, exclude, optional_fields, custom_fields
        )
        if key in self.schemas:
            return self.schemas[key]

        model_fields_list = list(self._selected_model_fields(model, fields, exclude))
        if optional_fields:
            if optional_fields == "__all__":
                optional_fields = [f.name for f in model_fields_list]

        definitions = {}
        for fld in model_fields_list:
            if fld.name in self.IGNORE_FIELDS:
                continue 
            python_type, field_info = get_schema_field(
                fld,
                depth=depth,
                optional=optional_fields and (fld.name in optional_fields),
            )
            definitions[fld.name] = (python_type, field_info)

        if custom_fields:
            for fld_name, python_type, field_info in custom_fields:
                # if not isinstance(field_info, FieldInfo):
                #     field_info = Field(field_info)
                definitions[fld_name] = (python_type, field_info)

        if name in self.schema_names:
            name = self._get_unique_name(name)
        
        schema: Type[Schema] = create_pydantic_model(
            name,
            __config__=ConfigDict(extra='forbid', from_attributes=True),
            __module__=base_class.__module__,
            __validators__={},
            **definitions,
        )  # type: ignore
        # __model_name: str,
        # *,
        # __config__: ConfigDict | None = None,
        # __base__: None = None,
        # __module__: str = __name__,
        # __validators__: dict[str, AnyClassMethod] | None = None,
        # __cls_kwargs__: dict[str, Any] | None = None,
        # **field_definitions: Any,
        self.schemas[key] = schema
        self.schema_names.add(name)
        return schema

factory = SchemaFactory()

create_schema = factory.create_schema