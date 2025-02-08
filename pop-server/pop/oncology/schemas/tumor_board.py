from ninja import Schema
from typing import Literal
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ConfigDict
from pydantic import Field, AliasChoices
from typing import List
from pop.oncology.models.tumor_board import (
    TumorBoardSpecialties,
    TumorBoard,
    UnspecifiedTumorBoard,
    MolecularTumorBoard,
    MolecularTherapeuticRecommendation,
)

TumorBoardBase: Schema = create_schema(
    TumorBoard, 
    exclude=(*CREATE_IGNORED_FIELDS,),
)

class TumorBoardSchema(TumorBoardBase, GetMixin):
    model_config = ConfigDict(title='TumorBoard')
    category: TumorBoardSpecialties = Field(description='Categorization of the tumor board by specialty')

UnspecifiedTumorBoardBase: Schema = create_schema(
    UnspecifiedTumorBoard, 
    exclude=(*CREATE_IGNORED_FIELDS, 'tumor_board'),
)

class UnspecifiedTumorBoardSchema(UnspecifiedTumorBoardBase, GetMixin):
    model_config = ConfigDict(title='UnspecifiedTumorBoard')
    category: Literal[TumorBoardSpecialties.UNSPECIFIED] = TumorBoardSpecialties.UNSPECIFIED # type: ignore

class UnspecifiedTumorBoardCreateSchema(UnspecifiedTumorBoardBase, CreateMixin):
    model_config = ConfigDict(title='UnspecifiedTumorBoardCreate')
    category: Literal[TumorBoardSpecialties.UNSPECIFIED] = TumorBoardSpecialties.UNSPECIFIED # type: ignore
    
    
MolecularTumorBoardBase: Schema = create_schema(
    MolecularTumorBoard, 
    exclude=(*CREATE_IGNORED_FIELDS, 'tumor_board'),
)

MolecularTherapeuticRecommendationBase: Schema = create_schema(
    MolecularTherapeuticRecommendation, 
    exclude=(*CREATE_IGNORED_FIELDS, 'molecular_tumor_board'),
)

class MolecularTherapeuticRecommendationSchema(MolecularTherapeuticRecommendationBase, GetMixin):
    model_config = ConfigDict(title='MolecularTherapeuticRecommendation')
    
class MolecularTherapeuticRecommendationCreateSchema(MolecularTherapeuticRecommendationBase, CreateMixin):
    model_config = ConfigDict(title='MolecularTherapeuticRecommendationCreate')

class MolecularTumorBoardSchema(MolecularTumorBoardBase, GetMixin):
    model_config = ConfigDict(title='MolecularTumorBoard')
    category: Literal[TumorBoardSpecialties.MOLECULAR] = TumorBoardSpecialties.MOLECULAR # type: ignore   
    therapeuticRecommendations: List[MolecularTherapeuticRecommendationSchema] = Field(
        description='Therapeutic recommendations of the molecular tumor board',
        alias='therapeutic_recommendations',
        validation_aliases=AliasChoices('therapeutic_recommendations','therapeuticRecommendations')
    ) 
    
class MolecularTumorBoardCreateSchema(MolecularTumorBoardBase, CreateMixin):
    model_config = ConfigDict(title='MolecularTumorBoardCreate')
    category: Literal[TumorBoardSpecialties.MOLECULAR] = TumorBoardSpecialties.MOLECULAR # type: ignore    

