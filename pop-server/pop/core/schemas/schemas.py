from datetime import datetime
from typing import Optional, List, Dict
from ninja import Schema, Field
from pydantic import ConfigDict, SecretStr
from django.contrib.auth import get_user_model
from ninja_jwt.schema import TokenObtainSlidingInputSchema, TokenObtainSlidingOutputSchema, TokenRefreshSlidingInputSchema, TokenRefreshSlidingOutputSchema
from typing_extensions import Annotated

UserModel = get_user_model()


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

    
class UserCredentialsSchema(TokenObtainSlidingInputSchema):
    username: str
    password: SecretStr
    # Schema config
    model_config = ConfigDict(
        title='UserCredentials',
    )

class OldSlidingTokenSchema(TokenRefreshSlidingInputSchema):
    # Schema config
    model_config = ConfigDict(
        title='OldSlidingToken',
    )

class NewSlidingTokenSchema(TokenRefreshSlidingOutputSchema):
    # Schema config
    model_config = ConfigDict(
        title='OldSlidingToken',
    )

class SlidingTokenSchema(TokenObtainSlidingOutputSchema):
    # Schema config
    model_config = ConfigDict(
        title='SlidingToken',
    )


class ResourceIdSchema(Schema):
    id: str 
    # Schema config
    model_config = ConfigDict(
        title='ResourceId',
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
