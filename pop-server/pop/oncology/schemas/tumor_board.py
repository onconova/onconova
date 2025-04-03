from pydantic import Field, AliasChoices
from typing import List, Literal

from pop.oncology import models as orm
from pop.oncology.models.tumor_board import TumorBoardSpecialties
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class UnspecifiedTumorBoardSchema(ModelGetSchema):
    category: Literal[TumorBoardSpecialties.UNSPECIFIED] = TumorBoardSpecialties.UNSPECIFIED # type: ignore
    config = SchemaConfig(model=orm.UnspecifiedTumorBoard, exclude=['tumor_board'])

class UnspecifiedTumorBoardCreateSchema(ModelCreateSchema):
    category: Literal[TumorBoardSpecialties.UNSPECIFIED] = TumorBoardSpecialties.UNSPECIFIED # type: ignore
    config = SchemaConfig(model=orm.UnspecifiedTumorBoard, exclude=['tumor_board'])

    
class MolecularTherapeuticRecommendationSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.MolecularTherapeuticRecommendation, exclude=['molecular_tumor_board'])

class MolecularTherapeuticRecommendationCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.MolecularTherapeuticRecommendation, exclude=['molecular_tumor_board'])

class MolecularTumorBoardSchema(ModelGetSchema):
    category: Literal[TumorBoardSpecialties.MOLECULAR] = TumorBoardSpecialties.MOLECULAR # type: ignore   
    therapeuticRecommendations: List[MolecularTherapeuticRecommendationSchema] = Field(
        description='Therapeutic recommendations of the molecular tumor board',
        alias='therapeutic_recommendations',
        validation_aliases=AliasChoices('therapeutic_recommendations','therapeuticRecommendations')
    ) 
    config = SchemaConfig(model=orm.MolecularTumorBoard, exclude=['tumor_board'])

class MolecularTumorBoardCreateSchema(ModelCreateSchema):
    category: Literal[TumorBoardSpecialties.MOLECULAR] = TumorBoardSpecialties.MOLECULAR # type: ignore    
    config = SchemaConfig(model=orm.MolecularTumorBoard, exclude=['tumor_board'])

