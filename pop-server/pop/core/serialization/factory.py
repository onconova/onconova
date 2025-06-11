from typing import Any,List, Tuple, Type, Optional
import types

from django.db.models import Model as DjangoModel

from pydantic import create_model as create_pydantic_model

from ninja.errors import ConfigError
from ninja.orm.factory import SchemaFactory as NinjaSchemaFactory
from ninja.schema import Schema

from .fields import get_schema_field, get_schema_field_filters
from .base import BaseSchema
from .filters import FilterBaseSchema
from .mixins import OrmMetadataMixin


__all__ = ["SchemaFactory", "factory", "create_schema"]

class SchemaFactory(NinjaSchemaFactory):
    """
    A factory for creating Pydantic schemas from Django models.

    This factory is a subclass of `ninja.orm.factory.SchemaFactory` and overrides
    the `create_schema` method to generate Pydantic schemas with custom fields
    and properties.

    Attributes:
        IGNORE_FIELDS (List[str]): A list of field names to ignore when creating schemas.
    """

    IGNORE_FIELDS = ['auto_id', ]
    
    def create_schema(
        self,
        model: Type[DjangoModel],
        *,
        name: str = "",
        depth: int = 0,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        expand: List[str] = None,
        reverse_fields: List[str] = None,
        optional_fields: Optional[List[str]] = None,
        custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
        bases: List[Type[Schema]] = [BaseSchema],
    ) -> Type[Schema]:
        
        name = name or model.__name__
        orm_metadata = {}
        if fields and exclude:
            raise ConfigError("Only one of 'fields' or 'exclude' should be set.")

        key = self.get_key(
            model, name, depth, fields, exclude, optional_fields, custom_fields
        )
        if key in self.schemas:
            return self.schemas[key]

        model_fields_list = list(self._selected_model_fields(model, fields, exclude))

        if reverse_fields: 
            model_fields_list.extend([model._meta.get_field(reverse_field) for reverse_field in reverse_fields])

        if optional_fields:
            if optional_fields == "__all__":
                optional_fields = [f.name for f in model_fields_list]

        definitions = {}
        resolvers = {}
        resolvers2 = {}
        for fld in model_fields_list:
            if fld.name in self.IGNORE_FIELDS:
                continue 
            resolver_fcn, field_name, (python_type, field_info) = get_schema_field(
                fld,
                expand=(expand or dict()).get(fld.name),
                optional=optional_fields and (fld.name in optional_fields),
                exclude_related_fields=exclude,
            )
            if resolver_fcn:
                resolvers[f'resolve_{field_name}'] = staticmethod(resolver_fcn)
                resolvers2[field_info.alias] = staticmethod(resolver_fcn)
            definitions[field_name] = (python_type, field_info)
            orm_metadata[field_name] = fld

        if custom_fields:
            for fld_name, python_type, field_info in custom_fields:
                definitions[fld_name] = (python_type, field_info)

        if name in self.schema_names:
            name = self._get_unique_name(name)

        schema: Type[Schema] = create_pydantic_model(
            name,
            __base__= (OrmMetadataMixin, *bases),
            __module__=bases[-1].__module__,
            __validators__={},
            **definitions,
        )
        for fcn_name, fcn in resolvers.items():
            setattr(schema, fcn_name, fcn) 
        # Store ORM metadata
        schema.set_orm_model(model)
        schema.set_orm_metadata(**orm_metadata)
        # Update the factory registry
        self.schemas[key] = schema
        self.schema_names.add(name)
        return schema


    def create_filters_schema(
        self,
        schema: Type[BaseSchema],
        *,
        name: str = "",
        depth: int = 0,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        base_class: Type[Schema] = FilterBaseSchema,
    ) -> Type[Schema]:

        name = name or schema.__name__
    
        if fields and exclude:
            raise ConfigError("Only one of 'fields' or 'exclude' should be set.")

        key = self.get_key(
            schema, name, depth, fields, exclude, None, None
        )
        if key in self.schemas:
            return self.schemas[key]

        definitions = {}
        filter_fcns = {}
        for field_name, field_info in schema.model_fields.items():
            if field_name in ['description', 'createdAt', 'createdBy', 'updatedBy', 'updatedAt', 'externalSourceId', 'externalSource', 'anonymized']:
                continue
            schema_fields = get_schema_field_filters(field_name, field_info)
            for field_name, (python_type, field_info), (method_name, filter_fcn) in schema_fields:
                definitions[field_name] = (python_type, field_info)
                filter_fcns[method_name] = filter_fcn

        if name in self.schema_names:
            name = self._get_unique_name(name)

        schema: Type[Schema] = create_pydantic_model(
            name,
            __base__=base_class,
            __module__=base_class.__module__,
            __validators__={},
            **definitions,
        )
        for fcn_name, fcn in filter_fcns.items():
            setattr(schema, fcn_name, types.MethodType(fcn, schema)) 
        self.schemas[key] = schema
        self.schema_names.add(name)
        return schema

factory = SchemaFactory()
create_schema = factory.create_schema
create_filters_schema = factory.create_filters_schema

