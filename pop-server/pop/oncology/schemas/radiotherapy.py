from pydantic import Field
from typing import List

from pop.oncology import models as orm
from pop.core.serialization.metaclasses import (
    ModelGetSchema,
    ModelCreateSchema,
    SchemaConfig,
)
from pop.core.anonymization import AnonymizationConfig


class RadiotherapyDosageSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.RadiotherapyDosage, exclude=["radiotherapy"])


class RadiotherapyDosageCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.RadiotherapyDosage, exclude=["radiotherapy"])


class RadiotherapySettingSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.RadiotherapySetting, exclude=["radiotherapy"])


class RadiotherapySettingCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.RadiotherapySetting, exclude=["radiotherapy"])


class RadiotherapySchema(ModelGetSchema):
    dosages: List[RadiotherapyDosageSchema] = Field(
        description="Radiation doses administered during the radiotherapy"
    )
    settings: List[RadiotherapySettingSchema] = Field(
        description="Settings of the radiotherapy irradiation procedure"
    )
    config = SchemaConfig(
        model=orm.Radiotherapy,
        anonymization=AnonymizationConfig(fields=["period"], key="caseId"),
    )


class RadiotherapyCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.Radiotherapy)
