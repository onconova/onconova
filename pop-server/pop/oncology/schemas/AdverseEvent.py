from pop.oncology.models import AdverseEvent, AdverseEventSuspectedCause, AdverseEventMitigation
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ModelFilterSchema
from ninja import Schema
from pydantic import Field, ConfigDict, AliasChoices
from typing import List 

AdverseEventBase: Schema = create_schema(
    AdverseEvent, 
    exclude=(*CREATE_IGNORED_FIELDS, 'is_resolved'),
)

AdverseEventSuspectedCauseBase: Schema = create_schema(
    AdverseEventSuspectedCause, 
    exclude=(*CREATE_IGNORED_FIELDS, 'adverse_event'),
)

AdverseEventMitigationBase: Schema = create_schema(
    AdverseEventMitigation, 
    exclude=(*CREATE_IGNORED_FIELDS, 'adverse_event'),
)


class AdverseEventSuspectedCauseSchema(AdverseEventSuspectedCauseBase, GetMixin):
    model_config = ConfigDict(title='AdverseEventSuspectedCause')

class AdverseEventSuspectedCauseCreateSchema(AdverseEventSuspectedCauseBase, CreateMixin):
    model_config = ConfigDict(title='AdverseEventSuspectedCauseCreate',)

class AdverseEventMitigationSchema(AdverseEventMitigationBase, GetMixin):
    model_config = ConfigDict(title='AdverseEventMitigation')

class AdverseEventMitigationCreateSchema(AdverseEventMitigationBase, CreateMixin):
    model_config = ConfigDict(title='AdverseEventMitigationCreate',)
    
class AdverseEventSchema(AdverseEventBase, GetMixin):
    model_config = ConfigDict(title='AdverseEvent')
    suspectedCauses: List[AdverseEventSuspectedCauseSchema] = Field(
        description='Suspected causes of the adverse event',
        alias='suspected_causes',
        validation_aliases=AliasChoices('suspected_causes','suspectedCauses')
    )
    mitigations: List[AdverseEventMitigationSchema] = Field(description='Mitigations of the adverse event')

class AdverseEventCreateSchema(AdverseEventBase, CreateMixin):
    model_config = ConfigDict(title='AdverseEventCreate')
    
    
