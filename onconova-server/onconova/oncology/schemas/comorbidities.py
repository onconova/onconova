from typing import List

from ninja import Field, Schema
from pydantic import AliasChoices

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.schemas import CodedConcept as CodedConceptSchema
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.core.types import Nullable
from onconova.oncology import models as orm


class ComorbiditiesAssessmentSchema(ModelGetSchema):
    score: Nullable[int | float] = Field(
        default=None,
        title="Score",
        description="Comorbidity score",
        alias="score",
    )
    config = SchemaConfig(
        model=orm.ComorbiditiesAssessment,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class ComorbiditiesAssessmentCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.ComorbiditiesAssessment)


class ComorbidityPanelCategory(Schema):
    label: str = Field(
        title="Label", description="Label of the comorbidity panel category"
    )
    default: Nullable[CodedConceptSchema] = Field(
        default=None, title="Default", description="Default choice for category"
    )
    conditions: List[CodedConceptSchema] = Field(
        title="Conditions",
        description="List of conditions included in the panel category",
    )


class ComorbiditiesPanel(Schema):
    name: str = Field(title="Name", description="Comorbidity panel name")
    categories: List[ComorbidityPanelCategory] = Field(
        title="Categories", description="Comorbidity panel categories"
    )
