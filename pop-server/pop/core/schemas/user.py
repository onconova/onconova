from pop.core import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig


class UserSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.User, exclude=['date_joined', 'groups', 'is_staff', 'is_superuser', 'user_permissions'])    

class UserCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.User, exclude=['date_joined', 'groups', 'is_staff', 'is_superuser', 'user_permissions'])    
