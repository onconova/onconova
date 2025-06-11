from typing import Literal
from pydantic import Field 

from pop.oncology import models as orm
from pop.oncology.models.staging import StagingDomain
from pop.core.schemas import CodedConcept as CodedConceptSchema
from pop.core.serialization.metaclasses import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.anonymization import AnonymizationConfig

class StagingSchema(ModelGetSchema):
    stagingDomain: StagingDomain = Field(title='Staging domain', description='Group or type of staging')
    stage: CodedConceptSchema = Field(description='Classification of the stage')
    config = SchemaConfig(model=orm.Staging, anonymization=AnonymizationConfig(fields=['date'], key='caseId'))


class TNMStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.TNM] = StagingDomain.TNM # type: ignore
    config = SchemaConfig(model=orm.TNMStaging, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class TNMStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.TNM] = StagingDomain.TNM # type: ignore
    config = SchemaConfig(model=orm.TNMStaging, exclude=['staging'])


class FIGOStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.FIGO] = StagingDomain.FIGO # type: ignore
    config = SchemaConfig(model=orm.FIGOStaging, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class FIGOStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.FIGO] = StagingDomain.FIGO # type: ignore
    config = SchemaConfig(model=orm.FIGOStaging, exclude=['staging'])


class BinetStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.BINET] = StagingDomain.BINET # type: ignore
    config = SchemaConfig(model=orm.BinetStaging, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class BinetStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.BINET] = StagingDomain.BINET # type: ignore
    config = SchemaConfig(model=orm.BinetStaging, exclude=['staging'])


class RaiStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.RAI] = StagingDomain.RAI # type: ignore
    config = SchemaConfig(model=orm.RaiStaging, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class RaiStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.RAI] = StagingDomain.RAI # type: ignore
    config = SchemaConfig(model=orm.RaiStaging, exclude=['staging'])


class BreslowDepthSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.BRESLOW] = StagingDomain.BRESLOW # type: ignore
    stage: CodedConceptSchema
    config = SchemaConfig(model=orm.BreslowDepth, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class BreslowDepthCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.BRESLOW] = StagingDomain.BRESLOW # type: ignore
    config = SchemaConfig(model=orm.BreslowDepth, exclude=['staging'])


class ClarkStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.CLARK] = StagingDomain.CLARK # type: ignore
    config = SchemaConfig(model=orm.ClarkStaging, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class ClarkStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.CLARK] = StagingDomain.CLARK # type: ignore
    config = SchemaConfig(model=orm.ClarkStaging, exclude=['staging'])


class ISSStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.ISS] = StagingDomain.ISS # type: ignore
    config = SchemaConfig(model=orm.ISSStaging, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class ISSStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.ISS] = StagingDomain.ISS # type: ignore
    config = SchemaConfig(model=orm.ISSStaging, exclude=['staging'])


class RISSStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.RISS] = StagingDomain.RISS # type: ignore
    config = SchemaConfig(model=orm.RISSStaging, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class RISSStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.RISS] = StagingDomain.RISS # type: ignore
    config = SchemaConfig(model=orm.RISSStaging, exclude=['staging'])


class GleasonGradeSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.GLEASON] = StagingDomain.GLEASON # type: ignore
    config = SchemaConfig(model=orm.GleasonGrade, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class GleasonGradeCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.GLEASON] = StagingDomain.GLEASON # type: ignore
    config = SchemaConfig(model=orm.GleasonGrade, exclude=['staging'])


class INSSStageSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.INSS] = StagingDomain.INSS # type: ignore
    config = SchemaConfig(model=orm.INSSStage, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class INSSStageCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.INSS] = StagingDomain.INSS # type: ignore
    config = SchemaConfig(model=orm.INSSStage, exclude=['staging'])


class INRGSSStageSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.INRGSS] = StagingDomain.INRGSS # type: ignore
    config = SchemaConfig(model=orm.INRGSSStage, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class INRGSSStageCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.INRGSS] = StagingDomain.INRGSS # type: ignore
    config = SchemaConfig(model=orm.INRGSSStage, exclude=['staging'])


class WilmsStageSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.WILMS] = StagingDomain.WILMS # type: ignore
    config = SchemaConfig(model=orm.WilmsStage, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class WilmsStageCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.WILMS] = StagingDomain.WILMS # type: ignore
    config = SchemaConfig(model=orm.WilmsStage, exclude=['staging'])


class RhabdomyosarcomaClinicalGroupSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.RHABDO] = StagingDomain.RHABDO # type: ignore
    config = SchemaConfig(model=orm.RhabdomyosarcomaClinicalGroup, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class RhabdomyosarcomaClinicalGroupCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.RHABDO] = StagingDomain.RHABDO # type: ignore
    config = SchemaConfig(model=orm.RhabdomyosarcomaClinicalGroup, exclude=['staging'])


class LymphomaStagingSchema(ModelGetSchema):
    stagingDomain: Literal[StagingDomain.LYMPHOMA] = StagingDomain.LYMPHOMA # type: ignore
    config = SchemaConfig(model=orm.LymphomaStaging, exclude=['staging'], anonymization=AnonymizationConfig(fields=['date'], key='caseId'))

class LymphomaStagingCreateSchema(ModelCreateSchema):
    stagingDomain: Literal[StagingDomain.LYMPHOMA] = StagingDomain.LYMPHOMA # type: ignore
    config = SchemaConfig(model=orm.LymphomaStaging, exclude=['staging'])

        