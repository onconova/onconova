from typing import Optional
from ninja import Field
from pydantic import AliasChoices

from pop.oncology import models as orm
from pop.core.measures import Measure
from pop.core.serialization.metaclasses import (
    ModelGetSchema,
    ModelCreateSchema,
    SchemaConfig,
)
from pop.core.anonymization import AnonymizationConfig


class VitalsSchema(ModelGetSchema):
    bodyMassIndex: Optional[Measure] = Field(
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
