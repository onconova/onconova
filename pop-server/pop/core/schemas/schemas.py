from datetime import date
from typing import Optional, List, Dict, Union
from uuid import UUID
from ninja import Schema
from psycopg.types.range import Range as PostgresRange
from pydantic import Field, ConfigDict, SecretStr,model_validator
from django.contrib.auth import get_user_model

from ninja_extra.schemas import NinjaPaginationResponseSchema
from ninja_jwt.schema import TokenObtainPairInputSchema, TokenObtainPairOutputSchema, TokenRefreshInputSchema, TokenRefreshOutputSchema

UserModel = get_user_model()

CREATE_IGNORED_FIELDS = (
    'id', 
    'created_at', 
    'updated_at', 
    'created_by', 
    'updated_by',
)  


class UserSchema(Schema):
    id: int
    username: str
    email: str
    firstName: Optional[str] = Field(default=None, alias='first_name')
    lastName: Optional[str] = Field(default=None, alias='last_name')
    # Schema config
    model_config = ConfigDict(
        title='User',
    )

    
class UserCredentialsSchema(TokenObtainPairInputSchema):
    username: str
    password: SecretStr
    # Schema config
    model_config = ConfigDict(
        title='UserCredentials',
    )

class TokenPairSchema(TokenObtainPairOutputSchema):

    # Schema config
    model_config = ConfigDict(
        title='TokenPair',
    )


class TokenRefreshSchema(TokenRefreshInputSchema):
    # Schema config
    model_config = ConfigDict(
        title='TokenRefresh',
    )

class RefreshedTokenPairSchema(TokenRefreshOutputSchema):
    # Schema config
    model_config = ConfigDict(
        title='RefreshedTokenPair',
    )

class Paginated(NinjaPaginationResponseSchema):
    pass

class ModifiedResourceSchema(Schema):
    id: UUID = Field()
    description: Optional[str] = Field(None)
    # Schema config
    model_config = ConfigDict(
        title='ModifiedResource',
    )

class CodedConceptSchema(Schema):  
    code: str
    system: str
    display: Optional[str] = None
    version: Optional[str] = None
    synonyms: Optional[List[str]] = None
    properties: Optional[Dict] = None
    # Schema config
    model_config = ConfigDict(
        title='CodedConcept',
    )


class RangeSchema(Schema):  
    start: Union[int, float]
    end: Optional[Union[int, float]] = None
    # Schema config
    model_config = ConfigDict(
        title='Range',
    )
    @model_validator(mode='before')
    def validate_data(cls, obj):
        range = obj._obj
        if isinstance(range, tuple):
            obj = {
                'start': range[0], 
                'end': range[1],
            }
        elif isinstance(range, PostgresRange):
            obj = {
                'start': range.lower, 
                'end': range.upper,
            }
        return obj
    
class PeriodSchema(Schema):  
    start: Optional[date] = None
    end: Optional[date] = None
    # Schema config
    model_config = ConfigDict(
        title='Period',
    )
    @model_validator(mode='before')
    def validate_data(cls, obj):
        period = obj._obj
        if isinstance(period, tuple):
            obj = {
                'start': period[0], 
                'end': period[1],
            }
        elif isinstance(period, PostgresRange):
            obj = {
                'start': period.lower, 
                'end': period.upper,
            }
        return obj