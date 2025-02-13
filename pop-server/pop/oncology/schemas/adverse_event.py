from typing import List 
from pydantic import Field, AliasChoices

from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class AdverseEventSuspectedCauseSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.AdverseEventSuspectedCause, exclude=('adverse_event',))

class AdverseEventSuspectedCauseCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.AdverseEventSuspectedCause, exclude=('adverse_event',))

class AdverseEventMitigationSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.AdverseEventMitigation, exclude=('adverse_event',))

class AdverseEventMitigationCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.AdverseEventMitigation, exclude=('adverse_event',))
    
class AdverseEventSchema(ModelGetSchema):
    suspectedCauses: List[AdverseEventSuspectedCauseSchema] = Field(
        description='Suspected causes of the adverse event',
        alias='suspected_causes',
        validation_aliases=AliasChoices('suspected_causes','suspectedCauses')
    )
    mitigations: List[AdverseEventMitigationSchema] = Field(
        description='Mitigations of the adverse event',
    )
    config = SchemaConfig(model=orm.AdverseEvent, exclude=('is_resolved',))    

class AdverseEventCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.AdverseEvent, exclude=('is_resolved',))    
    
    
