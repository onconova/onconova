from typing import Literal, List
from pydantic import Field
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept, Measure
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import staging as orm


class StagingCreate(BaseSchema):
    
    __orm_model__ = orm.Staging
    
    stagingDomain: orm.StagingDomain = Field(
        title="Staging domain", description="Group or type of staging"
    )
    externalSource: Nullable[str] = Field(
        None,
        description='The digital source of the data, relevant for automated data',
        title='External data source',
    )
    externalSourceId: Nullable[str] = Field(
        None,
        description='The data identifier at the digital source of the data, relevant for automated data',
        title='External data source Id',
    )
    caseId: UUID = Field(
        ...,
        description="Indicates the case of the patient who's cancer is staged",
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Clinically-relevant date at which the staging was performed and recorded.',
        title='Staging date',
    )
    stagedEntitiesIds: Nullable[List[UUID]] = Field(
        None,
        description='References to the neoplastic entities that were the focus of the staging.',
        title='Staged neoplastic entities',
    )
    

class Staging(StagingCreate, MetadataAnonymizationMixin):
    stage: CodedConcept = Field(
        title="Stage", 
        description="Classification of the stage"
    )
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"


class TNMStagingCreate(StagingCreate):
    
    __orm_model__ = orm.TNMStaging
    
    stagingDomain: Literal[orm.StagingDomain.TNM] = Field(
        orm.StagingDomain.TNM,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The classification of the TNM stage',
        title='TNM Stage',
        json_schema_extra={'x-terminology': 'TNMStage'},
    )
    methodology: Nullable[CodedConcept] = Field(
        None,
        description='Methodology used for TNM staging',
        title='TNM Staging methodology',
        json_schema_extra={'x-terminology': 'TNMStagingMethod'},
    )
    pathological: Nullable[bool] = Field(
        None,
        description='Whether the staging was based on pathological (true) or clinical (false) evidence.',
        title='Pathological staging',
    )
    primarytumor: Nullable[CodedConcept] = Field(
        None,
        description='T stage (extent of the primary tumor)',
        title='T Stage',
        json_schema_extra={'x-terminology': 'TNMPrimaryTumorCategory'},
    )
    regionalnodes: Nullable[CodedConcept] = Field(
        None,
        description='N stage (degree of spread to regional lymph nodes)',
        title='N Stage',
        json_schema_extra={'x-terminology': 'TNMRegionalNodesCategory'},
    )
    distantmetastases: Nullable[CodedConcept] = Field(
        None,
        description='M stage (presence of distant metastasis)',
        title='M Stage',
        json_schema_extra={'x-terminology': 'TNMDistantMetastasesCategory'},
    )
    grade: Nullable[CodedConcept] = Field(
        None,
        description='G stage (grade of the cancer cells)',
        title='G Stage',
        json_schema_extra={'x-terminology': 'TNMGradeCategory'},
    )
    residualtumor: Nullable[CodedConcept] = Field(
        None,
        description='R stage (extent of residual tumor cells after operation)',
        title='R Stage',
        json_schema_extra={'x-terminology': 'TNMResidualTumorCategory'},
    )
    lymphaticinvasion: Nullable[CodedConcept] = Field(
        None,
        description='L stage (invasion into lymphatic vessels)',
        title='L Stage',
        json_schema_extra={'x-terminology': 'TNMLymphaticInvasionCategory'},
    )
    venousinvasion: Nullable[CodedConcept] = Field(
        None,
        description='V stage (invasion into venous vessels)',
        title='V Stage',
        json_schema_extra={'x-terminology': 'TNMVenousInvasionCategory'},
    )
    perineuralinvasion: Nullable[CodedConcept] = Field(
        None,
        description='Pn stage (invasion into adjunct nerves)',
        title='Pn Stage',
        json_schema_extra={'x-terminology': 'TNMPerineuralInvasionCategory'},
    )
    serumtumormarkerlevel: Nullable[CodedConcept] = Field(
        None,
        description='S stage (serum tumor marker level)',
        title='S Stage',
        json_schema_extra={'x-terminology': 'TNMSerumTumorMarkerLevelCategory'},
    )

class TNMStaging(TNMStagingCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"



class FIGOStagingCreate(StagingCreate):
    
    __orm_model__ = orm.FIGOStaging
    
    stagingDomain: Literal[orm.StagingDomain.FIGO] = Field(
        orm.StagingDomain.FIGO,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the FIGO stage',
        title='FIGO Stage',
        json_schema_extra={'x-terminology': 'FIGOStage'},
    )
    methodology: Nullable[CodedConcept] = Field(
        None,
        description='Methodology used for the FIGO staging',
        title='FIGO staging methodology',
        json_schema_extra={'x-terminology': 'FIGOStagingMethod'},
    )

class FIGOStaging(FIGOStagingCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"


class BinetStagingCreate(StagingCreate):
    
    __orm_model__ = orm.Staging 
    
    stagingDomain: Literal[orm.StagingDomain.BINET] = Field(
        orm.StagingDomain.BINET,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the Binet stage',
        title='Binet Stage',
        json_schema_extra={'x-terminology': 'BinetStage'},
    )

class BinetStaging(BinetStagingCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"



class RaiStagingCreate(StagingCreate):
    
    __orm_model__ = orm.RaiStaging
    
    stagingDomain: Literal[orm.StagingDomain.RAI] = Field(
        orm.StagingDomain.RAI,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the Rai stage',
        title='Rai Stage',
        json_schema_extra={'x-terminology': 'RaiStage'},
    )
    methodology: Nullable[CodedConcept] = Field(
        None,
        description='Methodology used for the Rai staging',
        title='Rai staging methodology',
        json_schema_extra={'x-terminology': 'RaiStagingMethod'},
    )


class RaiStaging(RaiStagingCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"



class BreslowDepthCreate(StagingCreate):
    
    __orm_model__ = orm.BinetStaging

    stagingDomain: Literal[orm.StagingDomain.BRESLOW] = Field(
        orm.StagingDomain.BRESLOW,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    depth: Measure = Field(
        ...,
        description='Breslow depth',
        title='Breslow depth',
        json_schema_extra={
            'x-measure': 'Distance',
            'x-default-unit': 'mm',
        },
    )
    isUlcered: Nullable[bool] = Field(
        None,
        description='Whether the primary tumour presents ulceration',
        title='Ulcered',
    )


class BreslowDepth(BreslowDepthCreate, MetadataAnonymizationMixin):
    stage: CodedConcept = Field(
        title="Breslow Stage",
        description="The value of the Binet stage",
        json_schema_extra={"x-terminology": "BreslowDepthStage"},
    )
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"



class ClarkStagingCreate(StagingCreate):
    
    __orm_model__ = orm.ClarkStaging
    
    stagingDomain: Literal[orm.StagingDomain.CLARK] = Field(
        orm.StagingDomain.CLARK,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the Clark level stage',
        title='Clark Level Stage',
        json_schema_extra={'x-terminology': 'ClarkLevel'},
    )

class ClarkStaging(ClarkStagingCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"



class ISSStagingCreate(StagingCreate):
    
    __orm_model__ = orm.ISSStaging
    
    stagingDomain: Literal[orm.StagingDomain.ISS] = Field(
        orm.StagingDomain.ISS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of theISS stage',
        title='ISS Stage',
        json_schema_extra={'x-terminology': 'MyelomaISSStage'},
    )

class ISSStaging(ISSStagingCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    
    

class RISSStagingCreate(StagingCreate):
    
    __orm_model__ = orm.RISSStaging
    
    stagingDomain: Literal[orm.StagingDomain.RISS] = Field(
        orm.StagingDomain.RISS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the RISS stage',
        title='RISS Stage',
        json_schema_extra={'x-terminology': 'MyelomaRISSStage'},
    )

class RISSStaging(RISSStagingCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    


class GleasonGradeCreate(StagingCreate):
    
    __orm_model__ = orm.GleasonGrade
    
    stagingDomain: Literal[orm.StagingDomain.GLEASON] = Field(
        orm.StagingDomain.GLEASON,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the Gleason grade stage',
        title='Gleason grade Stage',
        json_schema_extra={'x-terminology': 'GleasonGradeGroupStage'},
    )

class GleasonGrade(GleasonGradeCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    


class INSSStageCreate(StagingCreate):
    
    __orm_model__ = orm.INSSStage
    
    stagingDomain: Literal[orm.StagingDomain.INSS] = Field(
        orm.StagingDomain.INSS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the INSS stage',
        title='INSS Stage',
        json_schema_extra={'x-terminology': 'NeuroblastomaINSSStage'},
    )


class INSSStage(INSSStageCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    


class INRGSSStageCreate(StagingCreate):
    
    __orm_model__ = orm.INRGSSStage
    
    stagingDomain: Literal[orm.StagingDomain.INRGSS] = Field(
        orm.StagingDomain.INRGSS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the INRGSS stage',
        title='INRGSS Stage',
        json_schema_extra={'x-terminology': 'NeuroblastomaINRGSSStage'},
    )
    
class INRGSSStage(INRGSSStageCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    


class WilmsStageCreate(StagingCreate):
    
    __orm_model__ = orm.WilmsStage
    
    stagingDomain: Literal[orm.StagingDomain.WILMS] = Field(
        orm.StagingDomain.WILMS,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the Wilms stage',
        title='Wilms Stage',
        json_schema_extra={'x-terminology': 'WilmsTumorStage'},
    )
    
class WilmsStage(WilmsStageCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    

class RhabdomyosarcomaClinicalGroupCreate(StagingCreate):
    
    __orm_model__ = orm.RhabdomyosarcomaClinicalGroup
    
    stagingDomain: Literal[orm.StagingDomain.RHABDO] = Field(
        orm.StagingDomain.RHABDO,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the rhabdomyosarcoma clinical group',
        title='Rhabdomyosarcoma clinical group',
        json_schema_extra={'x-terminology': 'RhabdomyosarcomaClinicalGroup'},
    )
    
class RhabdomyosarcomaClinicalGroup(RhabdomyosarcomaClinicalGroupCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    

class LymphomaStagingCreate(StagingCreate):
    
    __orm_model__ = orm.LymphomaStaging 
    
    stagingDomain: Literal[orm.StagingDomain.LYMPHOMA] = Field(
        orm.StagingDomain.LYMPHOMA,
        title="Staging domain",
        description="Staging domain discriminator category",
    )
    stage: CodedConcept = Field(
        ...,
        description='The value of the Lymphoma stage',
        title='Lymphoma Stage',
        json_schema_extra={'x-terminology': 'LymphomaStage'},
    )
    methodology: Nullable[CodedConcept] = Field(
        None,
        description='Methodology used for the Lymphoma staging',
        title='Lymphoma staging methodology',
        json_schema_extra={'x-terminology': 'LymphomaStagingMethod'},
    )
    bulky: Nullable[bool] = Field(
        None,
        description='Bulky modifier indicating if the lymphoma has the presence of bulky disease.',
        title='Bulky disease modifier',
    )
    pathological: Nullable[bool] = Field(
        None,
        description='Whether the staging was based on clinical or pathologic evidence.',
        title='Pathological staging',
    )
    modifiers: Nullable[List[CodedConcept]] = Field(
        None,
        description='Qualifier acting as modifier for the lymphoma stage',
        title='Lymphoma stage modifier',
        json_schema_extra={'x-terminology': 'LymphomaStageValueModifier'},
    )


class LymphomaStaging(LymphomaStagingCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    
