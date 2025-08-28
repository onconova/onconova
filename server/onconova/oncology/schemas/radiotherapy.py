from typing import List

from pydantic import Field

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.measures import Measure
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.oncology import models as orm


class RadiotherapyDosageSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.RadiotherapyDosage, exclude=["radiotherapy"])


class RadiotherapyDosageCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.RadiotherapyDosage, exclude=["radiotherapy"])


class RadiotherapySettingSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.RadiotherapySetting, exclude=["radiotherapy"])


class RadiotherapySettingCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.RadiotherapySetting, exclude=["radiotherapy"])


class RadiotherapySchema(ModelGetSchema):
    duration: Measure = Field(
        title="Duration",
        description="Duration of treatment",
        json_schema_extra={"x-measure": "Time"},
    )
    dosages: List[RadiotherapyDosageSchema] = Field(
        title="Dosages",
        description="Radiation doses administered during the radiotherapy",
    )
    settings: List[RadiotherapySettingSchema] = Field(
        title="Settings",
        description="Settings of the radiotherapy irradiation procedure",
    )
    config = SchemaConfig(
        model=orm.Radiotherapy,
        anonymization=AnonymizationConfig(fields=["period"], key="caseId"),
    )


class RadiotherapyCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Radiotherapy)
    config = SchemaConfig(model=orm.Radiotherapy)
