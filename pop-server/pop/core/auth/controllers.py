import json
from typing import Literal

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import resolve
from ninja import Query, Schema
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate
from pghistory.models import Events
from pop.core.auth import permissions as perms
from pop.core.auth.models import User
from pop.core.auth.schemas import UserCreateSchema, UserFilters
from pop.core.auth.schemas import UserPasswordReset as UserPasswordResetSchema
from pop.core.auth.schemas import UserProfileSchema, UserSchema
from pop.core.auth.token import XSessionTokenAuth
from pop.core.history.schemas import HistoryEvent
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema
from pop.core.schemas import Paginated
from pop.core.types import Nullable
from pop.core.utils import COMMON_HTTP_ERRORS
from pydantic import AliasChoices, Field


class UserCredentials(Schema):
    username: str
    password: str


class UserProviderClientToken(Schema):
    client_id: str
    id_token: Nullable[str] = None
    access_token: Nullable[str] = None


class UserProviderToken(Schema):
    provider: str
    process: Literal["login"] | Literal["connect"]
    token: UserProviderClientToken


class AuthenticationMeta(Schema):
    sessionToken: Nullable[str] = Field(
        default=None,
        alias="session_token",
        validation_alias=AliasChoices("sessionToken", "session_token"),
    )
    accessToken: Nullable[str] = Field(
        default=None,
        alias="access_token",
        validation_alias=AliasChoices("accessToken", "access_token"),
    )
    isAuthenticated: bool = Field(
        alias="is_authenticated",
        validation_alias=AliasChoices("isAuthenticated", "is_authenticated"),
    )


@api_controller(
    "/auth",
    tags=["Authentication"],
)
class AuthController(ControllerBase):

    @route.post(
        path="/session",
        response={
            200: AuthenticationMeta,
            401: None,
            400: None,
            403: None,
            500: None,
        },
        operation_id="login",
        openapi_extra=dict(security=[]),
    )
    def login(self, credentials: UserCredentials):
        """
        Login a user using basic authorization via username/password to obtain session token and/or access token.
        """
        view = resolve("/api/allauth/app/v1/auth/login")
        response = view.func(self.context.request)
        if response.status_code != 200:
            return response.status_code, None
        return 200, json.loads(response.content.decode())["meta"]

    @route.post(
        path="/provider/session",
        response={200: AuthenticationMeta, 400: None, 401: None, 500: None},
        operation_id="loginWithProviderToken",
        openapi_extra=dict(security=[]),
    )
    def login_with_provider_token(self, credentials: UserProviderToken):
        view = resolve("/api/allauth/app/v1/auth/provider/token")
        response = view.func(self.context.request)
        if response.status_code != 200:
            return response.status_code, None
        return 200, json.loads(response.content.decode())["meta"]


@api_controller(
    "/users",
    auth=[XSessionTokenAuth()],
    tags=["Users"],
)
class UsersController(ControllerBase):

    @route.get(
        path="",
        response={200: Paginated[UserSchema], **COMMON_HTTP_ERRORS},
        operation_id="getUsers",
    )
    @paginate
    @ordering
    def get_all_users_matching_the_query(self, query: Query[UserFilters]):  # type: ignore
        queryset = get_user_model().objects.all()
        return query.filter(queryset)

    @route.get(
        path="/{userId}",
        response={200: UserSchema, 404: None, **COMMON_HTTP_ERRORS},
        operation_id="getUserById",
    )
    def get_user_by_id(self, userId: str):
        return get_object_or_404(get_user_model(), id=userId)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageUsers],
        operation_id="createUser",
    )
    def create_user(self, payload: UserCreateSchema):
        return 201, payload.model_dump_django()

    @route.put(
        path="/{userId}",
        response={200: UserSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageUsers],
        operation_id="updateUser",
    )
    def update_user(self, userId: str, payload: UserCreateSchema):
        user = get_object_or_404(User, id=userId)
        return payload.model_dump_django(instance=user)

    @route.put(
        path="/{userId}/profile",
        response={201: UserSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageUsers | perms.IsRequestingUser],
        operation_id="updateUserProfile",
    )
    def update_user_profile(self, userId: str, payload: UserProfileSchema):
        user = get_object_or_404(User, id=userId)
        User.objects.filter(pk=user.id).update(**payload.model_dump(by_alias=True))
        return 201, get_object_or_404(User, id=user.id)

    @route.put(
        path="/{userId}/password",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        operation_id="updateUserPassword",
    )
    def update_user_password(self, userId: str, payload: UserPasswordResetSchema):
        user = get_object_or_404(User, id=userId)
        requesting_user = self.context.request.user
        authorized = user.id == requesting_user.id or requesting_user.can_manage_users
        if not authorized or not user.check_password(payload.oldPassword):
            return 403, None
        user.set_password(payload.newPassword)
        user.save()
        return 201, user

    @route.post(
        path="/{userId}/password/reset",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageUsers],
        operation_id="resetUserPassword",
    )
    def reset_user_password(self, userId: str, password: str):
        user = get_object_or_404(User, id=userId)
        user.set_password(password)
        user.save()
        return 201, user

    @route.get(
        path="/{userId}/events",
        response={200: Paginated[HistoryEvent], 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewUsers],
        operation_id="getUserEvents",
    )
    @paginate
    def get_user_events(self, userId: str):
        user = get_object_or_404(User, id=userId)
        return Events.objects.filter(pgh_context__username=user.username).order_by(
            "-pgh_created_at"
        )
