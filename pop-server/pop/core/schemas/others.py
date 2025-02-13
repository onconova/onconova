from datetime import date
from typing import Optional, List, Dict, Union
from uuid import UUID
from ninja import Schema
from psycopg.types.range import Range as PostgresRange
from pydantic import Field, model_validator, AliasChoices
from ninja_extra.schemas import NinjaPaginationResponseSchema

class Paginated(NinjaPaginationResponseSchema):
    pass
    
class ModifiedResource(Schema):
    id: UUID = Field(description='Unique identifier of the modified resource')
    description: Optional[str] = Field(None, description='A human-readable description of the modified resource')

class CodedConcept(Schema):  
    code: str = Field(description='Unique code within a coding system that identifies a concept')
    system: str = Field(description='The canonical URL of the code system defining the concept')
    display: Optional[str] = Field(default=None, description='Human readable description of the concept')
    version: Optional[str] = Field(default=None, description='Release version of the code system, if available')
    synonyms: Optional[List[str]] = Field(default=None, description='List of synonyms or alternative representations of the concept')
    properties: Optional[Dict] = Field(default=None, description='Other properties associated to the concept by the code system or otherwise')

class Range(Schema):  
    start: Union[int, float] = Field(description='The lower bound of the range')
    end: Optional[Union[int, float]] = Field(default=None, description='The upper bound of the range, if not exists, assumed to be unbounded')

    @model_validator(mode='before')
    def validate_data(cls, obj):
        range = obj._obj
        if isinstance(range, tuple):
            return {'start': range[0], 'end': range[1],}
        elif isinstance(range, PostgresRange):
            return {'start': range.lower, 'end': range.upper,}
        else:
            return obj
    
class Period(Schema):  
    start: Optional[date] = Field(default=None, description='The start date of the time period')
    end: Optional[date] = Field(default=None, description='The end date of the time period')

    @model_validator(mode='before')
    def validate_data(cls, obj):
        period = obj._obj
        if isinstance(period, tuple):
            return {'start': period[0], 'end': period[1],}
        elif isinstance(period, PostgresRange):
            return {'start': period.lower, 'end': period.upper,}
        else:
            return obj