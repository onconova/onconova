from pop.oncology import models as orm
from typing import Optional
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.schemas import CodedConceptSchema
from pydantic import Field, AliasChoices 


class NeoplasticEntitySchema(ModelGetSchema):

    topographyGroup: Optional[CodedConceptSchema] = Field(
        None,
        title='Topographical group', 
        alias='topography_group', 
        description='Broad anatomical location of the neoplastic entity',
        validation_alias=AliasChoices('topographyGroup','topography_group'),
    ) 
    config = SchemaConfig(model=orm.NeoplasticEntity)

class NeoplasticEntityCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.NeoplasticEntity)
