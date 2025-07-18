from typing import List

from ninja import Field, Schema
from pop.core.anonymization import AnonymizationConfig
from pop.core.schemas import CodedConcept as CodedConceptSchema
from pop.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from pop.core.types import Nullable
from pop.oncology import models as orm
from pydantic import AliasChoices


class ComorbiditiesAssessmentSchema(ModelGetSchema):
    score: Nullable[int | float] = Field(
        default=None, alias="score", description="Comorbidity score"
    )
    config = SchemaConfig(
        model=orm.ComorbiditiesAssessment,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class ComorbiditiesAssessmentCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.ComorbiditiesAssessment)


class ComorbidityPanelCategory(Schema):
    label: str = Field(description="Label of the comorbidity panel category")
    default: Nullable[CodedConceptSchema] = Field(
        None, description="Default choice for category"
    )
    conditions: List[CodedConceptSchema] = Field(
        description="List of conditions included in the panel category"
    )


class ComorbiditiesPanel(Schema):
    name: str = Field(description="Comorbidity panel name")
    categories: List[ComorbidityPanelCategory] = Field(
        None, description="Comorbidity panel categories"
    )
