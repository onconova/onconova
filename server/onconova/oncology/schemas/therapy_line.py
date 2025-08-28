from pydantic import AliasChoices, Field

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.schemas import Period as PeriodSchema
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.core.types import Nullable
from onconova.oncology import models as orm


class TherapyLineSchema(ModelGetSchema):
    period: Nullable[PeriodSchema] = Field(
        default=None,
        title="Period",
        description="Time period of the therapy line",
        alias="period",
    )
    label: str = Field(
        title="Label",
        description="Label categorizing the therapy line",
        alias="label",
    )
    progressionFreeSurvival: Nullable[float] = Field(
        default=None,
        title="Progression-free survival in months",
        description="Progression-free survival (PFS) of the patient for the therapy line",
        alias="progression_free_survival",
        validation_alias=AliasChoices(
            "progressionFreeSurvival", "progression_free_survival"
        ),
    )
    config = SchemaConfig(
        model=orm.TherapyLine,
        exclude=["label"],
        anonymization=AnonymizationConfig(fields=["period"], key="caseId"),
    )


class TherapyLineCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.TherapyLine, exclude=["label"])
    config = SchemaConfig(model=orm.TherapyLine, exclude=["label"])
