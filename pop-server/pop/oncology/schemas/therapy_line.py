from pop.core.anonymization import AnonymizationConfig
from pop.core.schemas import Period as PeriodSchema
from pop.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from pop.core.types import Nullable
from pop.oncology import models as orm
from pydantic import AliasChoices, Field


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
