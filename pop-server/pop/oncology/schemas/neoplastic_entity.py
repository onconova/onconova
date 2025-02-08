from pop.oncology.models import NeoplasticEntity
from pop.core.schemas import ModelSchema, CREATE_IGNORED_FIELDS
from pydantic import Field 


class NeoplasticEntitySchema(ModelSchema):
    description: str = Field(description='Human-readable description of the neoplastic entity') 

    class Meta:
        name = 'NeoplasticEntity'
        model = NeoplasticEntity
        fields = '__all__'

class NeoplasticEntityCreateSchema(ModelSchema):
    
    class Meta:
        name = 'NeoplasticEntityCreate'
        model = NeoplasticEntity
        exclude = (
            *CREATE_IGNORED_FIELDS,
        )


class NeoplasticEntityUpdateSchema(NeoplasticEntityCreateSchema):
    pass