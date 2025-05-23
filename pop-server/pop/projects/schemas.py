from pop.projects import models as orm
from pop.core.schemas.factory import create_filters_schema
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class ProjectSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.Project)

class ProjectCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Project)


ProjectFilters = create_filters_schema(schema = ProjectSchema, name='ProjectFilters')



class ProjectDataManagerGrantSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.ProjectDataManagerGrant)

class ProjectDataManagerGrantCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.ProjectDataManagerGrant, exclude=('project','member','granted_by','granted_at'))


ProjectDataManagerGrantFilters = create_filters_schema(schema = ProjectDataManagerGrantSchema, name='ProjectDataManagerGrantFilters')