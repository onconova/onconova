from ninja import Field
from pop.core.anonymization import AnonymizationConfig
from pop.core.measures import Measure
from pop.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from pop.core.types import Nullable
from pop.oncology import models as orm
from pydantic import AliasChoices


class VitalsSchema(ModelGetSchema):
    bodyMassIndex: Nullable[Measure] = Field(
        None,
        title="Body mass index",
        description="Bodymass index of the patient",
        alias="body_mass_index",
        validation_alias=AliasChoices("bodyMassIndex", "body_mass_index"),
    )
    config = SchemaConfig(
        model=orm.Vitals,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class VitalsCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Vitals)
