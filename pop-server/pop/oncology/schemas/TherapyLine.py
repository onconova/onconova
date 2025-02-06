from pop.oncology.models import TherapyLine
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ConfigDict, PeriodSchema
from ninja import Schema, Field
from pydantic import AliasChoices
from typing import Optional

TherapyLineBase: Schema = create_schema(
    TherapyLine, 
    exclude=(*CREATE_IGNORED_FIELDS, 'label'),
)

class TherapyLineSchema(TherapyLineBase, GetMixin):
    period: Optional[PeriodSchema] =  Field(
        None,
        title='Period',
        description='Time period of the therapy line', 
        alias='period',
    )    
    label: str = Field(
        title='Label',
        description='Label categorizing the therapy line', 
        alias='label',
    )       
    progressionFreeSurvival: Optional[float] = Field(
        None,
        title='Progression-free survival in months',
        description='Progression-free survival (PFS) of the patient for the therapy line', 
        alias='progression_free_survival',
        validation_alias=AliasChoices('progression_free_survival', 'progressionFreeSurvival')
    )   
    model_config = ConfigDict(title='TherapyLine')

class TherapyLineCreateSchema(TherapyLineBase, CreateMixin):
    model_config = ConfigDict(title='TherapyLineCreate')
