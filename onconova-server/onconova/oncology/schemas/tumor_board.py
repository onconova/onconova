from typing import List, Literal

from pydantic import AliasChoices, Field

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.oncology import models as orm
from onconova.oncology.models.tumor_board import TumorBoardSpecialties


class UnspecifiedTumorBoardSchema(ModelGetSchema):
    category: Literal[TumorBoardSpecialties.UNSPECIFIED] = Field(
        TumorBoardSpecialties.UNSPECIFIED,
        title="Category",
        description="Tumor board discriminator category",
    )
    config = SchemaConfig(
        model=orm.UnspecifiedTumorBoard,
        exclude=["tumor_board"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class UnspecifiedTumorBoardCreateSchema(ModelCreateSchema):
    category: Literal[TumorBoardSpecialties.UNSPECIFIED] = Field(
        TumorBoardSpecialties.UNSPECIFIED,
        title="Category",
        description="Tumor board discriminator category",
    )
    config = SchemaConfig(model=orm.UnspecifiedTumorBoard, exclude=["tumor_board"])


class MolecularTherapeuticRecommendationSchema(ModelGetSchema):
    config = SchemaConfig(
        model=orm.MolecularTherapeuticRecommendation, exclude=["molecular_tumor_board"]
    )


class MolecularTherapeuticRecommendationCreateSchema(ModelCreateSchema):
    config = SchemaConfig(
        model=orm.MolecularTherapeuticRecommendation, exclude=["molecular_tumor_board"]
    )


class MolecularTumorBoardSchema(ModelGetSchema):
    category: Literal[TumorBoardSpecialties.MOLECULAR] = Field(
        TumorBoardSpecialties.MOLECULAR,
        title="Category",
        description="Tumor board discriminator category",
    )
    therapeuticRecommendations: List[MolecularTherapeuticRecommendationSchema] = Field(
        title="Therapeutic Recommendations",
        description="Therapeutic recommendations of the molecular tumor board",
        alias="therapeutic_recommendations",
        validation_alias=AliasChoices(
            "therapeuticRecommendations", "therapeutic_recommendations"
        ),
    )
    config = SchemaConfig(
        model=orm.MolecularTumorBoard,
        exclude=["tumor_board"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class MolecularTumorBoardCreateSchema(ModelCreateSchema):
    category: Literal[TumorBoardSpecialties.MOLECULAR] = Field(
        TumorBoardSpecialties.MOLECULAR,
        title="Category",
        description="Tumor board discriminator category",
    )
    config = SchemaConfig(model=orm.MolecularTumorBoard, exclude=["tumor_board"])
    config = SchemaConfig(model=orm.MolecularTumorBoard, exclude=["tumor_board"])
