from pydantic import AliasChoices, Field

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.schemas import CodedConcept as CodedConceptSchema
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.core.types import Nullable
from onconova.oncology import models as orm


class PerformanceStatusSchema(ModelGetSchema):
    ecogInterpretation: Nullable[CodedConceptSchema] = Field(
        default=None,
        title="ECOG Interpreation",
        description="Official interpretation of the ECOG score",
        alias="ecog_interpretation",
        validation_alias=AliasChoices("ecogInterpretation", "ecog_interpretation"),
        json_schema_extra={"x-terminology": "ECOGPerformanceStatusInterpretation"},
    )
    karnofskyInterpretation: Nullable[CodedConceptSchema] = Field(
        default=None,
        title="Karnofsky Interpreation",
        description="Official interpretation of the Karnofsky score",
        alias="karnofsky_interpretation",
        validation_alias=AliasChoices(
            "karnofskyInterpretation", "karnofsky_interpretation"
        ),
        json_schema_extra={"x-terminology": "KarnofskyPerformanceStatusInterpretation"},
    )
    config = SchemaConfig(
        model=orm.PerformanceStatus,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class PerformanceStatusCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.PerformanceStatus)
    config = SchemaConfig(model=orm.PerformanceStatus)
