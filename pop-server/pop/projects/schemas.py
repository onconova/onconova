from pydantic import Field, AliasChoices
from pop.projects import models as orm
from pop.core.serialization.factory import create_filters_schema
from pop.core.serialization.metaclasses import ModelGetSchema, ModelCreateSchema, SchemaConfig
class ProjectSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.Project)

class ProjectCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Project)


ProjectFilters = create_filters_schema(schema = ProjectSchema, name='ProjectFilters')



class ProjectDataManagerGrantSchema(ModelGetSchema):
    isValid: bool = Field(
        title='Is valid',
        description='Whether the authorization grant is valid today',
        alias='is_valid',
        validation_alias=AliasChoices('isValid','is_valid'),        
    ) 
    config = SchemaConfig(model=orm.ProjectDataManagerGrant)

class ProjectDataManagerGrantCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.ProjectDataManagerGrant, exclude=('project','member'))


ProjectDataManagerGrantFilters = create_filters_schema(schema = ProjectDataManagerGrantSchema, name='ProjectDataManagerGrantFilters')