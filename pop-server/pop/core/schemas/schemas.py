from datetime import date
from typing import Optional, List, Dict
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

class ResourceIdSchema(Schema):
    id: str 
    # Schema config
    model_config = ConfigDict(
        title='ResourceId',
    )

class MeasureSchema(Schema):
    value: float
    unit: str

    # Schema config
    model_config = ConfigDict(
        title='Measure',
    )


class MeasureConversionSchema(Schema):
    value: float
    unit: str
    new_unit: str

    # Schema config
    model_config = ConfigDict(
        title='MeasureConversion',
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


class PeriodSchema(Schema):  
    start: date
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