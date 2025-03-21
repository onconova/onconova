from ninja import Query
from ninja_extra import route, api_controller, ControllerBase
from ninja_extra.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


from pop.core import permissions as perms
from pop.core.models import User
from pop.core.schemas import (
    Paginated,
    UserFilters,
    UserSchema, 
    UserCreateSchema,
    UserProfileSchema,
    UserPasswordResetSchema,
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
    def get_all_users_matching_the_query(self, query: Query[UserFilters]): # type: ignore
        queryset = get_user_model().objects.all()
        return query.filter(queryset)
    
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
        operation_id='updateUser',
    )
    def update_user(self, userId: str, payload: UserCreateSchema):
        user = get_object_or_404(User, id=userId)
        return payload.model_dump_django(instance=user)
        
    @route.put(
        path='/users/{userId}/password', 
       response={
            200: None,
            404: None,
            403: None,
        },
        operation_id='updateUserPassword',
    )
    def update_user_password(self, userId: str, payload: UserPasswordResetSchema):
        user = get_object_or_404(User, id=userId)
        requesting_user = self.context.request.user
        authorized = user.id == requesting_user.id or requesting_user.can_manage_users
        if not authorized or not user.check_password(payload.oldPassword):
            return 403, None
        user.set_password(payload.newPassword)
        user.save()
        return 200, None 
    

    @route.post(
        path='/users/{userId}/password/reset', 
        response={
            200: None,
        },
        permissions=[perms.CanManageUsers],
        operation_id='resetUserPassword',
    )
    def reset_user_password(self, userId: str, password: str):
        user = get_object_or_404(User, id=userId)
        user.set_password(password)
        user.save()
        return 200, None 

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
    