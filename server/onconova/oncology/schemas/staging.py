from typing import Literal

from pydantic import Field

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.schemas import CodedConcept as CodedConceptSchema
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.oncology import models as orm
from onconova.oncology.models.staging import StagingDomain


class StagingSchema(ModelGetSchema):
    stagingDomain: StagingDomain = Field(
        title="Staging domain", description="Group or type of staging"
    )
    stage: CodedConceptSchema = Field(
        title="Stage", description="Classification of the stage"
    )
    config = SchemaConfig(
        model=orm.Staging,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class TNMStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.TNM] = Field(
        StagingDomain.TNM,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.TNMStaging,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class TNMStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.TNM] = Field(
        StagingDomain.TNM,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.TNMStaging, exclude=["staging"])


class FIGOStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.FIGO] = Field(
        StagingDomain.FIGO,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.FIGOStaging,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class FIGOStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.FIGO] = Field(
        StagingDomain.FIGO,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.FIGOStaging, exclude=["staging"])


class BinetStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.BINET] = Field(
        StagingDomain.BINET,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.BinetStaging,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class BinetStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.BINET] = Field(
        StagingDomain.BINET,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.BinetStaging, exclude=["staging"])


class RaiStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.RAI] = Field(
        StagingDomain.RAI,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.RaiStaging,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class RaiStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.RAI] = Field(
        StagingDomain.RAI,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.RaiStaging, exclude=["staging"])


class BreslowDepthSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.BRESLOW] = Field(
        StagingDomain.BRESLOW,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConceptSchema = Field(
        title="Breslow Stage",
        description="The value of the Binet stage",
        json_schema_extra={"x-terminology": "BreslowDepthStage"},
    )
    config = SchemaConfig(
        model=orm.BreslowDepth,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class BreslowDepthCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.BRESLOW] = Field(
        StagingDomain.BRESLOW,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.BreslowDepth, exclude=["staging"])


class ClarkStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.CLARK] = Field(
        StagingDomain.CLARK,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.ClarkStaging,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class ClarkStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.CLARK] = Field(
        StagingDomain.CLARK,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.ClarkStaging, exclude=["staging"])


class ISSStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.ISS] = Field(
        StagingDomain.ISS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.ISSStaging,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class ISSStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.ISS] = Field(
        StagingDomain.ISS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.ISSStaging, exclude=["staging"])


class RISSStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.RISS] = Field(
        StagingDomain.RISS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.RISSStaging,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class RISSStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.RISS] = Field(
        StagingDomain.RISS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.RISSStaging, exclude=["staging"])


class GleasonGradeSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.GLEASON] = Field(
        StagingDomain.GLEASON,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.GleasonGrade,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class GleasonGradeCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.GLEASON] = Field(
        StagingDomain.GLEASON,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.GleasonGrade, exclude=["staging"])


class INSSStageSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.INSS] = Field(
        StagingDomain.INSS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.INSSStage,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class INSSStageCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.INSS] = Field(
        StagingDomain.INSS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.INSSStage, exclude=["staging"])


class INRGSSStageSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.INRGSS] = Field(
        StagingDomain.INRGSS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.INRGSSStage,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class INRGSSStageCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.INRGSS] = Field(
        StagingDomain.INRGSS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.INRGSSStage, exclude=["staging"])


class WilmsStageSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.WILMS] = Field(
        StagingDomain.WILMS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.WilmsStage,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class WilmsStageCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.WILMS] = Field(
        StagingDomain.WILMS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.WilmsStage, exclude=["staging"])


class RhabdomyosarcomaClinicalGroupSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.RHABDO] = Field(
        StagingDomain.RHABDO,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.RhabdomyosarcomaClinicalGroup,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class RhabdomyosarcomaClinicalGroupCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.RHABDO] = Field(
        StagingDomain.RHABDO,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.RhabdomyosarcomaClinicalGroup, exclude=["staging"])


class LymphomaStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.LYMPHOMA] = Field(
        StagingDomain.LYMPHOMA,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(
        model=orm.LymphomaStaging,
        exclude=["staging"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class LymphomaStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.LYMPHOMA] = Field(
        StagingDomain.LYMPHOMA,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    config = SchemaConfig(model=orm.LymphomaStaging, exclude=["staging"])
    config = SchemaConfig(model=orm.LymphomaStaging, exclude=["staging"])
