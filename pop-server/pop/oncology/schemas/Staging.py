from pop.oncology.models.Staging import (
    StagingDomain,
    Staging,
    FIGOStaging, 
    TNMStaging,
    BinetStaging,
    RaiStaging, 
    BreslowDepth, 
    ClarkStaging, 
    ISSStaging,
    RISSStaging, 
    GleasonGrade, 
    INSSStage, 
    INRGSSStage, 
    WilmsStage, 
    RhabdomyosarcomaClinicalGroup,
    LymphomaStaging
)
from pop.core.schemas import ModelSchema, CodedConceptSchema, CREATE_IGNORED_FIELDS
from typing import Literal
from pydantic import Field 

class StagingSchema(ModelSchema):
    stagingDomain: StagingDomain = Field(description='Staging domain')
    description: str = Field(description='Human-readable description of the staging') 
    stage: CodedConceptSchema = Field(description='Classificiation of the stage')

    class Meta:
        name = 'Staging'
        model = Staging
        fields = '__all__'

class TNMStagingSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.TNM] = StagingDomain.TNM # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'TNMStaging'
        model = TNMStaging
        exclude = [
            'staging',
        ]

class TNMStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.TNM] = StagingDomain.TNM # type: ignore

    class Meta:
        name = 'TNMStagingCreate'
        model = TNMStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class FIGOStagingSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.FIGO] = StagingDomain.FIGO # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'FIGOStaging'
        model = FIGOStaging
        exclude = [
            'staging',
        ]

class FIGOStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.FIGO] = StagingDomain.FIGO # type: ignore

    class Meta:
        name = 'FIGOStagingCreate'
        model = FIGOStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class BinetStagingSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.BINET] = StagingDomain.BINET # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'BinetStaging'
        model = BinetStaging
        exclude = [
            'staging',
        ]

class BinetStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.BINET] = StagingDomain.BINET # type: ignore

    class Meta:
        name = 'BinetStagingCreate'
        model = BinetStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]



class RaiStagingSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.RAI] = StagingDomain.RAI # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'RaiStaging'
        model = RaiStaging
        exclude = [
            'staging',
        ]

class RaiStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.RAI] = StagingDomain.RAI # type: ignore

    class Meta:
        name = 'RaiStagingCreate'
        model = RaiStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]



class BreslowDepthSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.BRESLOW] = StagingDomain.BRESLOW # type: ignore
    stage: CodedConceptSchema
    description: str = Field(description='Human-readable description of the staging') 
    
    class Meta:
        name = 'BreslowDepth'
        model = BreslowDepth
        exclude = [
            'staging',
        ]

class BreslowDepthCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.BRESLOW] = StagingDomain.BRESLOW # type: ignore

    class Meta:
        name = 'BreslowDepthCreate'
        model = BreslowDepth
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]
        



class ClarkStagingSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.CLARK] = StagingDomain.CLARK # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'ClarkStaging'
        model = ClarkStaging
        exclude = [
            'staging',
        ]

class ClarkStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.CLARK] = StagingDomain.CLARK # type: ignore

    class Meta:
        name = 'ClarkStagingCreate'
        model = ClarkStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]
    



class ISSStagingSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.ISS] = StagingDomain.ISS # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'ISSStaging'
        model = ISSStaging
        exclude = [
            'staging',
        ]

class ISSStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.ISS] = StagingDomain.ISS # type: ignore

    class Meta:
        name = 'ISSStagingCreate'
        model = ISSStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class RISSStagingSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.RISS] = StagingDomain.RISS # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'RISSStaging'
        model = RISSStaging
        exclude = [
            'staging',
        ]

class RISSStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.RISS] = StagingDomain.RISS # type: ignore

    class Meta:
        name = 'RISSStagingCreate'
        model = RISSStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]



class GleasonGradeSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.GLEASON] = StagingDomain.GLEASON # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'GleasonGrade'
        model = GleasonGrade
        exclude = [
            'staging',
        ]

class GleasonGradeCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.GLEASON] = StagingDomain.GLEASON # type: ignore

    class Meta:
        name = 'GleasonGradeCreate'
        model = GleasonGrade
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class INSSStageSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.INSS] = StagingDomain.INSS # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'INSSStage'
        model = INSSStage
        exclude = [
            'staging',
        ]

class INSSStageCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.INSS] = StagingDomain.INSS # type: ignore

    class Meta:
        name = 'INSSStageCreate'
        model = INSSStage
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class INRGSSStageSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.INRGSS] = StagingDomain.INRGSS # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'INRGSSStage'
        model = INRGSSStage
        exclude = [
            'staging',
        ]

class INRGSSStageCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.INRGSS] = StagingDomain.INRGSS # type: ignore

    class Meta:
        name = 'INRGSSStageCreate'
        model = INRGSSStage
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class WilmsStageSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.WILMS] = StagingDomain.WILMS # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'WilmsStage'
        model = WilmsStage
        exclude = [
            'staging',
        ]

class WilmsStageCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.WILMS] = StagingDomain.WILMS # type: ignore

    class Meta:
        name = 'WilmsStageCreate'
        model = WilmsStage
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class RhabdomyosarcomaClinicalGroupSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.RHABDO] = StagingDomain.RHABDO # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'RhabdomyosarcomaClinicalGroup'
        model = RhabdomyosarcomaClinicalGroup
        exclude = [
            'staging',
        ]

class RhabdomyosarcomaClinicalGroupCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.RHABDO] = StagingDomain.RHABDO # type: ignore

    class Meta:
        name = 'RhabdomyosarcomaClinicalGroupCreate'
        model = RhabdomyosarcomaClinicalGroup
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class LymphomaStagingSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.LYMPHOMA] = StagingDomain.LYMPHOMA # type: ignore
    description: str = Field(description='Human-readable description of the staging') 

    class Meta:
        name = 'LymphomaStaging'
        model = LymphomaStaging
        exclude = [
            'staging',
        ]

class LymphomaStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[StagingDomain.LYMPHOMA] = StagingDomain.LYMPHOMA # type: ignore

    class Meta:
        name = 'LymphomaStagingCreate'
        model = LymphomaStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]
        
        