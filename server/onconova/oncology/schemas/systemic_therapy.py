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


class SystemicTherapyMedicationSchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.SystemicTherapyMedication, exclude=["systemic_therapy"]
    )


class SystemicTherapyMedicationCreateSchema(ModelCreateSchema):
    config = SchemaConfig(
        model=orm.SystemicTherapyMedication, exclude=["systemic_therapy"]
    )


class SystemicTherapySchema(ModelGetSchema):
    medications: List[SystemicTherapyMedicationSchema] = Field(
        title="Medications",
        description="Medications administered during the systemic therapy",
    )
    duration: Measure = Field(
        title="Duration",
        description="Duration of treatment",
        json_schema_extra={"x-measure": "Time"},
    )
    config = SchemaConfig(
        model=orm.SystemicTherapy,
        anonymization=AnonymizationConfig(fields=["period"], key="caseId"),
    )


class SystemicTherapyCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.SystemicTherapy, exclude=["is_adjunctive"])
    config = SchemaConfig(model=orm.SystemicTherapy, exclude=["is_adjunctive"])
