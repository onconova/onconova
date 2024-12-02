from datetime import datetime

from ninja_extra import route, api_controller, permissions
from ninja_jwt.controller import TokenObtainPairController

from pop.core.schemas import (
    UserSchema, 
    NewSlidingTokenSchema, 
    OldSlidingTokenSchema,
    SlidingTokenSchema, 
    UserCredentialsSchema
)
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from typing import List 

@api_controller("/auth", tags=["Auth"])
class AuthController(TokenObtainPairController):
    auto_import = False

    @route.post(
        "/sliding",
        response=SlidingTokenSchema,
        url_name="token_obtain_sliding",
        operation_id="getSlidingToken",
    )
    def obtain_token(self, user_credentials: UserCredentialsSchema):
        user_credentials.check_user_authentication_rule()
        return user_credentials.to_response_schema()

    @route.post(
        "/sliding/refresh",
        response=NewSlidingTokenSchema,
        url_name="token_refresh_sliding",
        operation_id="refereshSlidingToken",
    )
    def refresh_token(self, refresh_token: OldSlidingTokenSchema):
        return refresh_token.to_response_schema()
    
    @route.get(
        path="/users",
        operation_id='getUsers',
        response={
            200: List[UserSchema]
        }, 
    )
    def get_all_users_matching_the_query(self):
        return get_user_model().objects.all()
    
    @route.get(
        path="/users/{userId}", 
        operation_id='getUserById',
        response={
            200: UserSchema,
            404: None
        }, 
    )
    def get_user_by_id(self, userId: int):
        return get_object_or_404(get_user_model(), id=userId)
    