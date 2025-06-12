from pydantic import Field, AliasChoices

from pop.research.models import project as orm
from pop.core.serialization.factory import create_filters_schema
from pop.core.serialization.metaclasses import ModelGetSchema, ModelCreateSchema, SchemaConfig

class ProjectSchema(ModelGetSchema):
    """
    Schema for retrieving a research project record.
    """
    config = SchemaConfig(model=orm.Project)

class ProjectCreateSchema(ModelCreateSchema):
    """
    Schema for creating a new research project record.
    """
    config = SchemaConfig(model=orm.Project)


# Filter schema for project search queries
ProjectFilters = create_filters_schema(
    schema = ProjectSchema, 
    name='ProjectFilters'
)


class ProjectDataManagerGrantSchema(ModelGetSchema):
    """
    Schema for retrieving a project data manager grant record.
    Includes additional computed properties.
    """
    isValid: bool = Field(
        title='Is valid',
        description='Whether the authorization grant is valid today',
        alias='is_valid',
        validation_alias=AliasChoices('isValid','is_valid'),        
    ) 
    config = SchemaConfig(model=orm.ProjectDataManagerGrant)

class ProjectDataManagerGrantCreateSchema(ModelCreateSchema):
    """
    Schema for creating a new project data manager grant record.
    Excludes project and member fields, as those are usually set by the system.
    """
    config = SchemaConfig(model=orm.ProjectDataManagerGrant, exclude=('project','member'))


# Filter schema for project data manager grant search queries
ProjectDataManagerGrantFilters = create_filters_schema(
    schema = ProjectDataManagerGrantSchema, 
    name='ProjectDataManagerGrantFilters'
)