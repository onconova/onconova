from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from ninja.schema import Field, ResolverMetaclass
from pop.core.anonymization import AnonymizationConfig, AnonymizationMixin
from pop.core.models import BaseModel as OrmBaseModel
from pop.core.serialization.base import BaseSchema
from pop.core.serialization.factory import create_schema
from pop.core.types import Nullable
from pydantic import AliasChoices
from pydantic.dataclasses import dataclass

# Track whether the base ModelSchema classes have been declared
_is_modelschema_class_defined = False

# Fields to automatically exclude when for create-type resources
CREATE_IGNORED_FIELDS = ("id",)

# Fields to automatically include when for get-type resources
GET_SCHEMA_FIELDS = (
    ("description", str, Field(title="Description", description="Human-readable description")),
)


# Fields to automatically include when for event-tracked resources
METADATA_FIELDS = (
    (
        "createdAt",
        Nullable[datetime],
        Field(
            default=None,
            title="Created at", 
            description="Date-time when the resource was created",
            alias="created_at",
            validation_alias=AliasChoices("createdAt", "created_at"),
        ),
    ),
    (
        "updatedAt",
        Nullable[datetime],
        Field(
            default=None,
            title="Updated at", 
            description="Date-time when the resource was last updated",
            alias="updated_at",
            validation_alias=AliasChoices("updatedAt", "updated_at"),
        ),
    ),
    (
        "createdBy",
        Nullable[str],
        Field(
            default=None,
            title="Created by", 
            description="Username of the user who created the resource",
            alias="created_by",
            validation_alias=AliasChoices("createdBy", "created_by"),
        ),
    ),
    (
        "updatedBy",
        Nullable[List[str]],
        Field(
            default=None,
            title="Updated by", 
            description="Usernames of the users who have updated the resource",
            alias="updated_by",
            validation_alias=AliasChoices("updatedBy", "updated_by"),
        ),
    ),
)


@dataclass
class SchemaConfig:
    """
    Configuration class for defining model schema generation behavior.

    Attributes:
        model (Any): ORM model class.
        anonymization (Optional[AnonymizationConfig]): Optional anonymization config.
        schema_name (Optional[str]): Explicit schema class name.
        fields (Optional[List[str] | Tuple[str]]): Specific fields to include.
        exclude (Optional[List[str] | Tuple[str]]): Fields to exclude.
        expand (Optional[Dict]): Additional schema expansions.
    """

    model: Any
    anonymization: AnonymizationConfig | None = None
    schema_name: str | None = None
    fields: List[str] | Tuple[str] | None = None
    exclude: List[str] | Tuple[str] | None = None
    expand: Dict | None = None


class ModelSchemaMetaclassBase(ResolverMetaclass):
    """
    Metaclass for dynamically generating Ninja schemas from ORM models.

    Handles:
    - Custom fields injection (e.g. description, timestamps, audit fields)
    - Anonymization mixin integration
    - Exclude rules for create schemas
    - Schema naming conventions
    """

    def __new__(
        mcs,
        name: str,
        bases: tuple,
        namespace: dict,
        **kwargs,
    ):
        # Extract the metaclass configuration from the namespace
        metaclass_config: SchemaConfig = namespace.pop("config", None)

        # Construct base metaclass
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
                and issubclass(base, (ModelGetSchema, ModelCreateSchema))
                and base in (ModelGetSchema, ModelCreateSchema)
            ):
                # Get the fields defined on the metaclass' namespace
                custom_fields = []
                annotations = namespace.get("__annotations__", {})
                for attr_name, type in annotations.items():
                    if attr_name.startswith("_"):
                        continue
                    default = namespace.get(attr_name, ...)
                    custom_fields.append((attr_name, type, default))

                # If it is a get schema, add description field to the custom schema fields
                if issubclass(base, ModelGetSchema) and issubclass(
                    metaclass_config.model, OrmBaseModel
                ):
                    custom_fields.extend(GET_SCHEMA_FIELDS)
                    if hasattr(metaclass_config.model, "pgh_event_model"):
                        custom_fields.extend(METADATA_FIELDS)

                # If it is a creation schema, add the ignored model fields to the exclude list
                exclude = list(metaclass_config.exclude or [])
                if issubclass(base, ModelCreateSchema) and issubclass(
                    metaclass_config.model, OrmBaseModel
                ):
                    exclude.extend(list(CREATE_IGNORED_FIELDS))

                # If the new schema's name was not specified, base it on the model name by default
                schema_name = metaclass_config.schema_name or (
                    metaclass_config.model.__name__
                    + ("Create" if issubclass(base, ModelCreateSchema) else "")
                )

                schema_bases: List[object] = [cls]
                if metaclass_config.anonymization:
                    schema_bases.append(AnonymizationMixin)

                # Construct the schema from the model dynamically
                model_schema = create_schema(
                    metaclass_config.model,
                    name=schema_name,
                    fields=list(metaclass_config.fields or []),
                    exclude=exclude,
                    expand=metaclass_config.expand,
                    custom_fields=custom_fields,
                    bases=tuple(schema_bases),
                )
                model_schema.__doc__ = cls.__doc__

                # If anonymization config is provided, set it up
                if metaclass_config.anonymization:
                    AnonymizationMixin._setup(
                        model_schema, metaclass_config.anonymization
                    )

                return model_schema
        return cls


class ModelGetSchema(BaseSchema, metaclass=ModelSchemaMetaclassBase):
    """
    Base schema for retrieving model data.

    Uses ModelSchemaMetaclassBase to dynamically generate fields from the ORM model.
    """

    pass


class ModelCreateSchema(BaseSchema, metaclass=ModelSchemaMetaclassBase):
    """
    Base schema for creating model data.

    Excludes system-managed fields (like 'id') and uses ModelSchemaMetaclassBase.
    """

    pass


# Mark that schema base classes have now been declared
_is_modelschema_class_defined = True
