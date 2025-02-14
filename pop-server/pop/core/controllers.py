from ninja_extra import route, api_controller, ControllerBase
from ninja_extra.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from typing import List 


from pop.core import permissions as perms
from pop.core.models import User
from pop.core.schemas import (
    Paginated,
    UserSchema, 
    UserCreateSchema,
    UserProfileSchema,
    ModifiedResourceSchema,
    TokenRefresh, 
    RefreshedTokenPair,
    TokenPair, 
    UserCredentials
)

@api_controller(
    "/auth/token", 
    tags=["Auth"]
)
class AuthController(ControllerBase):

    @route.post(
        "/pair",
        response=TokenPair,
        operation_id="getTokenPair",
    )
    def obtain_token_pair(self, credentials: UserCredentials):
        credentials.check_user_authentication_rule()
        return credentials.to_response_schema()

    @route.post(
        "/refresh",
        response=RefreshedTokenPair,
        operation_id="refreshTokenPair",
    )
    def refresh_token_pair(self, refresh_token: TokenRefresh):
        return refresh_token.to_response_schema()
    
    
@api_controller(
    '/auth', 
    auth=[JWTAuth()], 
    tags=['Auth'],  
)
class UsersController(ControllerBase):

    @route.get(
        path="/users",
        response={
            200: Paginated[UserSchema]
        }, 
        permissions=[perms.CanViewUsers],
        operation_id='getUsers',
    )
    @paginate
    def get_all_users_matching_the_query(self):
        return get_user_model().objects.all()
    
    @route.get(
        path="/users/{userId}", 
        response={
            200: UserSchema,
            404: None
        }, 
        permissions=[perms.CanViewUsers],
        operation_id='getUserById',
    )
    def get_user_by_id(self, userId: str):
        return get_object_or_404(get_user_model(), id=userId)


    @route.post(
        path="/users", 
        response={
            201: ModifiedResourceSchema,
        }, 
        permissions=[perms.CanManageUsers],
        operation_id='createUser',
    )
    def create_user(self, payload: UserCreateSchema):
        return payload.model_dump_django()

    @route.put(
        path='/users/{userId}', 
       response={
            200: UserSchema,
            404: None,
        },
        permissions=[perms.CanManageUsers],
        operation_id='UpdateUser',
    )
    def update_user(self, userId: str, payload: UserCreateSchema):
        return payload.model_dump_django(instance=get_object_or_404(User, id=userId))

    
    @route.put(
        path='/users/{userId}/profile', 
       response={
            200: UserSchema,
            404: None,
        },
        permissions=[perms.CanManageUsers | perms.IsRequestingUser],
        operation_id='updateUserProfile',
    )
    def update_user_profile(self, userId: str, payload: UserProfileSchema):
        user = get_object_or_404(User, id=userId)
        User.objects.filter(pk=user.id).update(**payload.model_dump(by_alias=True))
        return get_object_or_404(User, id=user.id)
    