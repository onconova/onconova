from pydantic import AliasChoices, Field

from onconova.core.serialization.factory import create_filters_schema
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.research.models import project as orm


class ProjectSchema(ModelGetSchema):
    """
    This schema is used to serialize and deserialize data related to research projects.
    It binds the `onconova.research.models.Project` ORM model to automatically generate fields.
    """

    config = SchemaConfig(model=orm.Project)


class ProjectCreateSchema(ModelCreateSchema):
    """
    Schema for creating a new Project instance.
    It binds the `onconova.research.models.Project` ORM model to automatically generate fields.
    """

    config = SchemaConfig(model=orm.Project)


# Filter schema for project search queries
ProjectFilters = create_filters_schema(
    schema=ProjectSchema,
    name="ProjectFilters",
)


class ProjectDataManagerGrantSchema(ModelGetSchema):
    """
    Schema for retrieving a project data manager grant record.
    It binds the `onconova.research.models.ProjectDataManagerGrant` ORM model to automatically generate fields.
    """

    isValid: bool = Field(
        title="Is valid",
        description="Whether the authorization grant is valid today",
        alias="is_valid",
        validation_alias=AliasChoices("isValid", "is_valid"),
    )
    config = SchemaConfig(model=orm.ProjectDataManagerGrant)


class ProjectDataManagerGrantCreateSchema(ModelCreateSchema):
    """
    Schema for creating a new project data manager grant record.
    It binds the `onconova.research.models.ProjectDataManagerGrant` ORM model to automatically generate fields.
    """

    config = SchemaConfig(
        model=orm.ProjectDataManagerGrant, exclude=["project", "member"]
    )


# Filter schema for project data manager grant search queries
ProjectDataManagerGrantFilters = create_filters_schema(
    schema=ProjectDataManagerGrantSchema, name="ProjectDataManagerGrantFilters"
)
