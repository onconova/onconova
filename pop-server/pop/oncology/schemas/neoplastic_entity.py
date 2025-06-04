from pop.oncology import models as orm
from typing import Optional
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.anonymization import AnonymizationConfig
from pop.core.schemas import CodedConceptSchema
from pydantic import Field, AliasChoices 


class NeoplasticEntitySchema(ModelGetSchema):

    topographyGroup: Optional[CodedConceptSchema] = Field(
        None,
        title='Topographical group', 
        alias='topography_group', 
        description='Broad anatomical location of the neoplastic entity',
        validation_alias=AliasChoices('topographyGroup','topography_group'),
        json_schema_extra={
            'x-terminology': 'CancerTopographyGroup',
        },
    ) 
    config = SchemaConfig(model=orm.NeoplasticEntity, anonymization=AnonymizationConfig(fields=['assertionDate'], key='caseId'))

class NeoplasticEntityCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.NeoplasticEntity)
