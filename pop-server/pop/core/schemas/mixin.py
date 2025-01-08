
from pydantic import Field, BaseModel as PydanticBase
from pop.core.models import BaseModel
from pop.core.schemas.schemas import CREATE_IGNORED_FIELDS 
from pop.core.schemas.metaclass import ModelSchema 

class BaseModelSchema(ModelSchema):
    class Meta:
        model=BaseModel 
        fields=(*CREATE_IGNORED_FIELDS,)

class GetMixin(BaseModelSchema):
    description: str = Field(description='Human-readable description') 
    
class CreateMixin(PydanticBase):
    pass        