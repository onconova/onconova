from pop.oncology.models import NeoplasticEntity
from pop.core.schemas import ModelSchema
from pydantic import Field 


class NeoplasticEntitySchema(ModelSchema):
    description: str = Field(description='HUman-readable description of the neoplastic entity') 

    class Meta:
        name = 'NeoplasticEntity'
        model = NeoplasticEntity
        fields = '__all__'

class NeoplasticEntityCreateSchema(ModelSchema):
    
    class Meta:
        name = 'NeoplasticEntityCreate'
        model = NeoplasticEntity
        exclude = (
            'id', 
            'created_at', 
            'updated_at', 
            'created_by', 
            'updated_by',
        )


class NeoplasticEntityUpdateSchema(NeoplasticEntityCreateSchema):
    pass