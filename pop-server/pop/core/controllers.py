from ninja_extra import route, api_controller, ControllerBase
from ninja_jwt.authentication import JWTAuth

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from typing import List 


from pop.core.schemas import (
    UserSchema, 
    TokenRefreshSchema, 
    RefreshedTokenPairSchema,
    TokenPairSchema, 
    UserCredentialsSchema
)

@api_controller(
    "/auth/token", 
    tags=["Auth"]
)
class AuthController(ControllerBase):

    @route.post(
        "/pair",
        response=TokenPairSchema,
        operation_id="getTokenPair",
    )
    def obtain_token_pair(self, credentials: UserCredentialsSchema):
        credentials.check_user_authentication_rule()
        return credentials.to_response_schema()

    @route.post(
        "/refresh",
        response=RefreshedTokenPairSchema,
        operation_id="refreshTokenPair",
    )
    def refresh_token_pair(self, refresh_token: TokenRefreshSchema):
        return refresh_token.to_response_schema()
    
    
@api_controller(
    '/auth', 
    auth=[JWTAuth()], 
    tags=['Auth'],  
)
class UsersController(ControllerBase):

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


