from pydantic import Field
from typing import List

from pop.oncology import models as orm
from pop.core.measures import Measure
from pop.core.serialization.metaclasses import (
    ModelGetSchema,
    ModelCreateSchema,
    SchemaConfig,
)
from pop.core.anonymization import AnonymizationConfig


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
        description="Medications administered during the systemic therapy"
    )
    duration: Measure = Field(description="Duration of treatment")
    config = SchemaConfig(
        model=orm.SystemicTherapy,
        anonymization=AnonymizationConfig(fields=["period"], key="caseId"),
    )


class SystemicTherapyCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.SystemicTherapy, exclude=["is_adjunctive"])
