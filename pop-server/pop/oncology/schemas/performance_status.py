from typing import Optional
from pydantic import Field, AliasChoices

from pop.oncology import models as orm
from pop.core.schemas import CodedConceptSchema
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class PerformanceStatusSchema(ModelGetSchema):
    ecogInterpretation: Optional[CodedConceptSchema] = Field(
            description='Official interpretation of the ECOG score',
            alias='ecog_interpretation',
            validation_alias=AliasChoices('ecogInterpretation', 'ecog_interpretation'),
    )
    karnofskyInterpretation: Optional[CodedConceptSchema] = Field(
        description='Official interpretation of the Karnofsky score',
        alias='karnofsky_interpretation',
        validation_alias=AliasChoices('karnofskyInterpretation', 'karnofsky_interpretation'),
    )
    config = SchemaConfig(model=orm.PerformanceStatus)


class PerformanceStatusCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.PerformanceStatus)