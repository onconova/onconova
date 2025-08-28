import types
from typing import Any, List, Optional, Tuple, Type

from ninja.errors import ConfigError
from ninja.orm.factory import SchemaFactory as NinjaSchemaFactory
from ninja.schema import Schema
from pydantic import create_model as create_pydantic_model

from onconova.core.models import BaseModel

from .base import BaseSchema
from .fields import SchemaFieldDefinition, get_schema_field, get_schema_field_filters
from .filters import FilterBaseSchema

__all__ = ["SchemaFactory", "factory", "create_schema"]


class SchemaFactory(NinjaSchemaFactory):
    """
    A factory class for dynamically creating Pydantic schema classes based on ORM models.

    This class extends `NinjaSchemaFactory` and provides methods to generate Pydantic models
    (schemas) for serialization and deserialization of ORM models, as well as filter schemas
    for querying.

    Attributes:
        IGNORE_FIELDS (List[str]): List of model field names to ignore when generating schemas.

    Methods:
        create_schema(
            Dynamically creates a Pydantic schema class for the given ORM model.
            Allows customization of included/excluded fields, optional fields, custom fields,
            and base classes. Handles field resolvers and ORM metadata.

        create_filters_schema(
            Dynamically creates a filter schema class based on an existing schema.
            Used for building query filters, with support for field inclusion/exclusion
            and custom filter resolvers.
    """

    IGNORE_FIELDS = [
        "auto_id",
    ]

    def create_schema(
        self,
        model: Type[BaseModel],
        *,
        name: str = "",
        depth: int = 0,
        fields: List[str] | None = None,
        exclude: List[str] | None = None,
        expand: dict | None = None,
        reverse_fields: List[str] | None = None,
        optional_fields: Optional[List[str]] = None,
        custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
        bases: Tuple[Any, ...] = tuple(),
    ) -> Type[Schema]:
        """
        Dynamically creates a Pydantic schema class for a given ORM model.

        Args:
            model (Type[BaseModel]): The ORM model class to generate the schema for.
            name (str, optional): The name of the generated schema class. Defaults to the model's class name.
            depth (int, optional): The depth for nested/related fields expansion. Defaults to 0.
            fields (List[str], optional): List of field names to include in the schema. Mutually exclusive with `exclude`.
            exclude (List[str], optional): List of field names to exclude from the schema. Mutually exclusive with `fields`.
            expand (dict, optional): Dictionary specifying related fields to expand in the schema.
            reverse_fields (List[str], optional): List of reverse relation field names to include.
            optional_fields (Optional[List[str]], optional): List of field names to mark as optional, or "__all__" for all fields.
            custom_fields (Optional[List[Tuple[str, Any, Any]]], optional): List of custom fields to add, each as (name, type, FieldInfo).
            bases (Tuple[Any, ...], optional): Additional base classes for the generated schema.

        Returns:
            Type[Schema]: The dynamically generated Pydantic schema class.

        Raises:
            ConfigError: If both `fields` and `exclude` are provided.

        Notes:
            - The generated schema is cached and reused if the same parameters are provided.
            - Custom resolvers for fields are attached as static methods.
            - ORM metadata is stored on the schema for later use.
        """

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
            model_fields_list.extend(
                [
                    model._meta.get_field(reverse_field)
                    for reverse_field in reverse_fields
                ]
            )

        if optional_fields:
            if optional_fields == "__all__":
                optional_fields = [f.name for f in model_fields_list]

        definitions = {}
        resolvers = {}
        resolvers2 = {}
        for fld in model_fields_list:
            if fld.name in self.IGNORE_FIELDS:
                continue
            field_definition: SchemaFieldDefinition = get_schema_field(
                fld,
                expand=(expand or dict()).get(fld.name),
                optional=bool(optional_fields and (fld.name in optional_fields)),
                exclude_related_fields=exclude,
            )
            if field_definition.resolver_fcn:
                resolvers[f"resolve_{field_definition.name}"] = staticmethod(
                    field_definition.resolver_fcn
                )
                resolvers2[field_definition.name] = staticmethod(
                    field_definition.resolver_fcn
                )
            definitions[field_definition.name] = (
                field_definition.python_type,
                field_definition.field_info,
            )
            orm_metadata[field_definition.name] = fld

        if custom_fields:
            for fld_name, python_type, field_info in custom_fields:
                definitions[fld_name] = (python_type, field_info)

        if name in self.schema_names:
            name = self._get_unique_name(name)

        if BaseSchema not in bases and not any(
            [issubclass(base, BaseSchema) for base in bases]
        ):
            bases = (BaseSchema, *bases)
        schema: Type[BaseSchema] = create_pydantic_model(
            name,
            __base__=bases,
            __module__=BaseSchema.__module__,
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
        schema: Type[Any],
        *,
        name: str = "",
        depth: int = 0,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        base_class: Type[Schema] = FilterBaseSchema,
    ) -> Type[Schema]:
        """
        Dynamically creates a Pydantic schema class for filtering based on the fields of the given schema.

        Args:
            schema (Type[Any]): The base Pydantic schema class to generate filters for.
            name (str, optional): The name of the generated filter schema. Defaults to the name of the input schema.
            depth (int, optional): The depth for nested schema generation. Defaults to 0.
            fields (Optional[List[str]], optional): List of field names to include in the filter schema. Mutually exclusive with `exclude`.
            exclude (Optional[List[str]], optional): List of field names to exclude from the filter schema. Mutually exclusive with `fields`.
            base_class (Type[Schema], optional): The base class to use for the generated filter schema. Defaults to FilterBaseSchema.

        Raises:
            ConfigError: If both `fields` and `exclude` are provided.

        Returns:
            Type[Schema]: The dynamically generated Pydantic schema class for filtering.
        """

        name = name or schema.__name__

        if fields and exclude:
            raise ConfigError("Only one of 'fields' or 'exclude' should be set.")

        key = self.get_key(schema, name, depth, fields, exclude, None, None)
        if key in self.schemas:
            return self.schemas[key]

        definitions = {}
        filter_fcns = {}
        for field_name, field_info in schema.model_fields.items():
            if exclude and field_name in exclude:
                continue
            if field_name in [
                "description",
                "createdBy",
                "updatedBy",
                "externalSourceId",
                "anonymized",
            ]:
                continue
            schema_fields_definitions = get_schema_field_filters(field_name, field_info)
            for definition in schema_fields_definitions:
                definitions[definition.name] = (
                    definition.python_type,
                    definition.field_info,
                )
                if definition.resolver_fcn:
                    filter_fcns[f"filter_{definition.name.replace('.','_')}"] = (
                        definition.resolver_fcn
                    )
                    definition.resolver_fcn = (
                        None  # Clear resolver to avoid duplication in schema
                    )

        if name in self.schema_names:
            name = self._get_unique_name(name)

        filter_schema: Type[Schema] = create_pydantic_model(
            name,
            __base__=base_class,
            __module__=base_class.__module__,
            __validators__={},
            **definitions,
        )
        for fcn_name, fcn in filter_fcns.items():
            setattr(filter_schema, fcn_name, types.MethodType(fcn, filter_schema))
        self.schemas[key] = filter_schema
        self.schema_names.add(name)
        return filter_schema


factory = SchemaFactory()
create_schema = factory.create_schema
create_filters_schema = factory.create_filters_schema
