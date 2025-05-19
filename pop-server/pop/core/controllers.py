import requests
import os 
from typing import Any, Optional
from ninja import Query, Schema
from ninja_extra import status,route, api_controller, ControllerBase
from ninja_extra.pagination import paginate

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


from pop.core import permissions as perms
from pop.core.security import XSessionTokenAuth
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

class OAuthExchangeCode(Schema):
    code: str
    provider: str
    state: Optional[str] = None
    redirect_uri: Optional[str] = None


@api_controller(
    "/auth", 
    tags=["Auth"]
)
class AuthController(ControllerBase):

    @route.post(
        "/pair",
        response=TokenPair,
        operation_id="getTokenPair",
        openapi_extra=dict(security=[])
    )
    def obtain_token_pair(self, credentials: UserCredentials):
        credentials.check_user_authentication_rule()
        return credentials.to_response_schema()

    @route.post(
        "/refresh",
        response=RefreshedTokenPair,
        operation_id="refreshTokenPair",
        openapi_extra=dict(security=[])
    )
    def refresh_token_pair(self, refresh_token: TokenRefresh):
        return refresh_token.to_response_schema()


    @route.post(
        path="/oauth/access_token", 
        response={
            200: Any,
            400: Any
        }, 
        openapi_extra=dict(security=[]),
        operation_id='exchangeOauthCodeForAccessToken',
    )
    def exchange_oauth_code_for_access_token(self, payload: OAuthExchangeCode):
        print('payload', payload)
        provider = payload.provider

        if provider == 'github':
            token_url = 'https://github.com/login/oauth/access_token'
            client_id = os.getenv('POP_GITHUB_CLIENT_ID')
            client_secret = os.getenv('POP_GITHUB_SECRET')

            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': payload.code,
            }
            print('DATA', data)
            headers = {'Accept': 'application/json'}
            response = requests.post(token_url, params=data, headers=headers)
            print(response.url)
            if response.status_code == 200:
                tokens = response.json()
                # Now — use AllAuth's headless provider/token endpoint or your own logic to log them in
                return 200, tokens
            else:
                return 400, {'error': 'Token exchange failed.', 'details': response.json()}

        else:
            return 400, {'error': 'Unsupported provider.'}
    

    
@api_controller(
    '/users', 
    auth=[XSessionTokenAuth()], 
    tags=['Auth'],  
)
class UsersController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[UserSchema],
            401: None, 403: None,
        }, 
        operation_id='getUsers',
    )
    @paginate
    def get_all_users_matching_the_query(self, query: Query[UserFilters]): # type: ignore
        queryset = get_user_model().objects.all()
        return query.filter(queryset)
    
    @route.get(
        path="/{userId}", 
        response={
            200: UserSchema,
            404: None, 401: None, 403: None,
        }, 
        operation_id='getUserById',
    )
    def get_user_by_id(self, userId: str):
        return get_object_or_404(get_user_model(), id=userId)


    @route.post(
        path="", 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        }, 
        permissions=[perms.CanManageUsers],
        operation_id='createUser',
    )
    def create_user(self, payload: UserCreateSchema):
        return 201, payload.model_dump_django()

    @route.put(
        path='/{userId}', 
       response={
            200: UserSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageUsers],
        operation_id='updateUser',
    )
    def update_user(self, userId: str, payload: UserCreateSchema):
        user = get_object_or_404(User, id=userId)
        return payload.model_dump_django(instance=user)
        
    @route.put(
        path='/{userId}/profile', 
       response={
            200: UserSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageUsers | perms.IsRequestingUser],
        operation_id='updateUserProfile',
    )
    def update_user_profile(self, userId: str, payload: UserProfileSchema):
        user = get_object_or_404(User, id=userId)
        User.objects.filter(pk=user.id).update(**payload.model_dump(by_alias=True))
        return get_object_or_404(User, id=user.id)
    
    @route.put(
        path='/{userId}/password', 
       response={
            200: None,
            404: None, 401: None, 403: None,
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
        path='/{userId}/password/reset', 
        response={
            200: None,
            401: None, 403: None,
        },
        permissions=[perms.CanManageUsers],
        operation_id='resetUserPassword',
    )
    def reset_user_password(self, userId: str, password: str):
        user = get_object_or_404(User, id=userId)
        user.set_password(password)
        user.save()
        return 200, None 
