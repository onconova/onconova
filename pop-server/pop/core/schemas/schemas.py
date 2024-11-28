from datetime import datetime
from typing import Optional, List, Dict
from ninja import Schema
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class UserSchema(Schema):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_staff: bool
    is_superuser: bool

class UserTokenSchema(Schema):
    token: str
    user: UserSchema
    token_exp_date: Optional[datetime]

class ResourceIdSchema(Schema):
    id: str 
    
class ReferenceSchema(Schema):
    type: str = None
    id: str = None
    url: Optional[str] = None

class CodedConceptSchema(Schema):  
    code: str
    system: str
    display: Optional[str] = None
    version: Optional[str] = None
    synonyms: Optional[List[str]] = None
    properties: Optional[Dict] = None
