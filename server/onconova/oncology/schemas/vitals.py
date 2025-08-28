from ninja import Field
from pydantic import AliasChoices

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.measures import Measure
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.core.types import Nullable
from onconova.oncology import models as orm


class VitalsSchema(ModelGetSchema):
    bodyMassIndex: Nullable[Measure] = Field(
        None,
        title="Body mass index",
        description="Bodymass index of the patient",
        alias="body_mass_index",
        validation_alias=AliasChoices("bodyMassIndex", "body_mass_index"),
        json_schema_extra={"x-measure": "MassPerArea"},
    )
    config = SchemaConfig(
        model=orm.Vitals,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class VitalsCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Vitals)
    config = SchemaConfig(model=orm.Vitals)
