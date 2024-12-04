from pop.oncology.models.Staging import (
    FIGO, FIGOStaging, 
    TNM, TNMStaging,
    BINET, BinetStaging,
    RAI, RaiStaging, 
    BRESLOW, BreslowDepth, 
    CLARK, ClarkStaging, 
    ISS, ISSStaging,
    RISS, RISSStaging, 
    GLEASON, GleasonGrade, 
    INSS, INSSStage, 
    INRGSS, INRGSSStage, 
    WILMS, WilmsStage, 
    RHABDO, RhabdomyosarcomaClinicalGroup,
    LYMPHOMA, LymphomaStaging
)
from pop.core.schemas import ModelSchema, CodedConceptSchema, CREATE_IGNORED_FIELDS
from typing import Literal
from pydantic import Field 

class TNMStagingSchema(ModelSchema):
    stagingDomain: Literal[TNM] = TNM # type: ignore

    class Meta:
        name = 'TNMStaging'
        model = TNMStaging
        exclude = [
            'staging',
        ]

class TNMStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[TNM] = TNM # type: ignore

    class Meta:
        name = 'TNMStagingCreate'
        model = TNMStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class FIGOStagingSchema(ModelSchema):
    stagingDomain: Literal[FIGO] = FIGO # type: ignore

    class Meta:
        name = 'FIGOStaging'
        model = FIGOStaging
        exclude = [
            'staging',
        ]

class FIGOStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[FIGO] = FIGO # type: ignore

    class Meta:
        name = 'FIGOStagingCreate'
        model = FIGOStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class BinetStagingSchema(ModelSchema):
    stagingDomain: Literal[BINET] = BINET # type: ignore

    class Meta:
        name = 'BinetStaging'
        model = BinetStaging
        exclude = [
            'staging',
        ]

class BinetStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[BINET] = BINET # type: ignore

    class Meta:
        name = 'BinetStagingCreate'
        model = BinetStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]



class RaiStagingSchema(ModelSchema):
    stagingDomain: Literal[RAI] = RAI # type: ignore

    class Meta:
        name = 'RaiStaging'
        model = RaiStaging
        exclude = [
            'staging',
        ]

class RaiStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[RAI] = RAI # type: ignore

    class Meta:
        name = 'RaiStagingCreate'
        model = RaiStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]



class BreslowDepthSchema(ModelSchema):
    stagingDomain: Literal[BRESLOW] = BRESLOW # type: ignore
    stage: CodedConceptSchema
    
    class Meta:
        name = 'BreslowDepth'
        model = BreslowDepth
        exclude = [
            'staging',
        ]

class BreslowDepthCreateSchema(ModelSchema):
    stagingDomain: Literal[BRESLOW] = BRESLOW # type: ignore

    class Meta:
        name = 'BreslowDepthCreate'
        model = BreslowDepth
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]
        



class ClarkStagingSchema(ModelSchema):
    stagingDomain: Literal[CLARK] = CLARK # type: ignore

    class Meta:
        name = 'ClarkStaging'
        model = ClarkStaging
        exclude = [
            'staging',
        ]

class ClarkStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[CLARK] = CLARK # type: ignore

    class Meta:
        name = 'ClarkStagingCreate'
        model = ClarkStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]
    



class ISSStagingSchema(ModelSchema):
    stagingDomain: Literal[ISS] = ISS # type: ignore

    class Meta:
        name = 'ISSStaging'
        model = ISSStaging
        exclude = [
            'staging',
        ]

class ISSStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[ISS] = ISS # type: ignore

    class Meta:
        name = 'ISSStagingCreate'
        model = ISSStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class RISSStagingSchema(ModelSchema):
    stagingDomain: Literal[RISS] = RISS # type: ignore

    class Meta:
        name = 'RISSStaging'
        model = RISSStaging
        exclude = [
            'staging',
        ]

class RISSStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[RISS] = RISS # type: ignore

    class Meta:
        name = 'RISSStagingCreate'
        model = RISSStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]



class GleasonGradeSchema(ModelSchema):
    stagingDomain: Literal[GLEASON] = GLEASON # type: ignore

    class Meta:
        name = 'GleasonGrade'
        model = GleasonGrade
        exclude = [
            'staging',
        ]

class GleasonGradeCreateSchema(ModelSchema):
    stagingDomain: Literal[GLEASON] = GLEASON # type: ignore

    class Meta:
        name = 'GleasonGradeCreate'
        model = GleasonGrade
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class INSSStageSchema(ModelSchema):
    stagingDomain: Literal[INSS] = INSS # type: ignore

    class Meta:
        name = 'INSSStage'
        model = INSSStage
        exclude = [
            'staging',
        ]

class INSSStageCreateSchema(ModelSchema):
    stagingDomain: Literal[INSS] = INSS # type: ignore

    class Meta:
        name = 'INSSStageCreate'
        model = INSSStage
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class INRGSSStageSchema(ModelSchema):
    stagingDomain: Literal[INRGSS] = INRGSS # type: ignore

    class Meta:
        name = 'INRGSSStage'
        model = INRGSSStage
        exclude = [
            'staging',
        ]

class INRGSSStageCreateSchema(ModelSchema):
    stagingDomain: Literal[INRGSS] = INRGSS # type: ignore

    class Meta:
        name = 'INRGSSStageCreate'
        model = INRGSSStage
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class WilmsStageSchema(ModelSchema):
    stagingDomain: Literal[WILMS] = WILMS # type: ignore

    class Meta:
        name = 'WilmsStage'
        model = WilmsStage
        exclude = [
            'staging',
        ]

class WilmsStageCreateSchema(ModelSchema):
    stagingDomain: Literal[WILMS] = WILMS # type: ignore

    class Meta:
        name = 'WilmsStageCreate'
        model = WilmsStage
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class RhabdomyosarcomaClinicalGroupSchema(ModelSchema):
    stagingDomain: Literal[RHABDO] = RHABDO # type: ignore

    class Meta:
        name = 'RhabdomyosarcomaClinicalGroup'
        model = RhabdomyosarcomaClinicalGroup
        exclude = [
            'staging',
        ]

class RhabdomyosarcomaClinicalGroupCreateSchema(ModelSchema):
    stagingDomain: Literal[RHABDO] = RHABDO # type: ignore

    class Meta:
        name = 'RhabdomyosarcomaClinicalGroupCreate'
        model = RhabdomyosarcomaClinicalGroup
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]


class LymphomaStagingSchema(ModelSchema):
    stagingDomain: Literal[LYMPHOMA] = LYMPHOMA # type: ignore

    class Meta:
        name = 'LymphomaStaging'
        model = LymphomaStaging
        exclude = [
            'staging',
        ]

class LymphomaStagingCreateSchema(ModelSchema):
    stagingDomain: Literal[LYMPHOMA] = LYMPHOMA # type: ignore

    class Meta:
        name = 'LymphomaStagingCreate'
        model = LymphomaStaging
        exclude = [
            *CREATE_IGNORED_FIELDS,
            'staging',
        ]
        
        