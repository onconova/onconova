from typing import List

from pydantic import AliasChoices, Field

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.oncology import models as orm


class AdverseEventSuspectedCauseSchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.AdverseEventSuspectedCause, exclude=("adverse_event",)
    )


class AdverseEventSuspectedCauseCreateSchema(ModelCreateSchema):
    config = SchemaConfig(
        model=orm.AdverseEventSuspectedCause, exclude=("adverse_event",)
    )


class AdverseEventMitigationSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.AdverseEventMitigation, exclude=("adverse_event",))


class AdverseEventMitigationCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.AdverseEventMitigation, exclude=("adverse_event",))


class AdverseEventSchema(ModelGetSchema):
    suspectedCauses: List[AdverseEventSuspectedCauseSchema] = Field(
        title="Suspected causes",
        description="Suspected causes of the adverse event",
        alias="suspected_causes",
        validation_alias=AliasChoices("suspectedCauses", "suspected_causes"),
    )
    mitigations: List[AdverseEventMitigationSchema] = Field(
        title="Mitigations",
        description="Mitigations of the adverse event",
    )
    config = SchemaConfig(
        model=orm.AdverseEvent,
        exclude=("is_resolved",),
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class AdverseEventCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.AdverseEvent, exclude=("is_resolved",))
    config = SchemaConfig(model=orm.AdverseEvent, exclude=("is_resolved",))
