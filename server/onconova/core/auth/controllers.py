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
from pydantic import AliasChoices, Field

from onconova.core.auth import permissions as perms
from onconova.core.auth.models import User
from onconova.core.auth.schemas import UserCreateSchema, UserFilters
from onconova.core.auth.schemas import (
    UserPasswordReset as UserPasswordResetSchema, 
    AuthenticationMeta, 
    UserProviderToken, 
    UserProfileSchema, 
    UserSchema, 
    UserCredentials,
)
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.history.schemas import HistoryEvent
from onconova.core.schemas import ModifiedResource as ModifiedResourceSchema
from onconova.core.schemas import Paginated
from onconova.core.types import Nullable
from onconova.core.utils import COMMON_HTTP_ERRORS



@api_controller(
    "/auth",
    tags=["Authentication"],
)
class AuthController(ControllerBase):
    """API controller to handle authentication-related endpoints for user login and session management."""

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
        Authenticates a user using the provided credentials.
        """
        # The request is routed internally to the Django-Allauth `allauth/app/v1/auth/login` endpoint to actually handle the authentication.
        view = resolve("/api/allauth/app/v1/auth/login")
        assert self.context and self.context.request
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
        """
        Authenticates a user using a provider token. 
        """
        # The request is routed internally to the Django-Allauth `allauth/app/v1/auth/provider/token` endpoint to actually handle the authentication.
        view = resolve("/api/allauth/app/v1/auth/provider/token")
        assert self.context and self.context.request
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
    """
    Controller for managing user-related operations.
    """

    @route.get(
        path="",
        response={200: Paginated[UserSchema], **COMMON_HTTP_ERRORS},
        operation_id="getUsers",
    )
    @paginate()
    @ordering()
    def get_all_users_matching_the_query(self, query: Query[UserFilters]):  # type: ignore
        """
        Retrieves all user objects that match the specified query filters.
        """
        queryset = get_user_model().objects.all()
        return query.filter(queryset)

    @route.get(
        path="/{userId}",
        response={200: UserSchema, 404: None, **COMMON_HTTP_ERRORS},
        operation_id="getUserById",
    )
    def get_user_by_id(self, userId: str):
        """
        Retrieve a user instance by its unique ID.
        """
        return get_object_or_404(get_user_model(), id=userId)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageUsers],
        operation_id="createUser",
    )
    def create_user(self, payload: UserCreateSchema):
        """
        Creates a new user with the provided payload.
        """
        return 201, payload.model_dump_django()

    @route.put(
        path="/{userId}",
        response={200: UserSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageUsers],
        operation_id="updateUser",
    )
    def update_user(self, userId: str, payload: UserCreateSchema):
        """
        Updates the specified user's information using the provided payload.
        """
        user = get_object_or_404(User, id=userId)
        return payload.model_dump_django(instance=user)

    @route.put(
        path="/{userId}/profile",
        response={201: UserSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageUsers | perms.IsRequestingUser],
        operation_id="updateUserProfile",
    )
    def update_user_profile(self, userId: str, payload: UserProfileSchema):
        """
        Updates the profile information of a user with the given user ID.
        """
        user = get_object_or_404(User, id=userId)
        User.objects.filter(pk=user.id).update(**payload.model_dump(by_alias=True))
        return 201, get_object_or_404(User, id=user.id)

    @route.put(
        path="/{userId}/password",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        operation_id="updateUserPassword",
    )
    def update_user_password(self, userId: str, payload: UserPasswordResetSchema):
        """
        Updates the password for a specified user.
        """
        user = get_object_or_404(User, id=userId)
        assert self.context and self.context.request
        requesting_user: User = self.context.request.user  # type: ignore
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
        """
        Resets the password for the specified user.
        """
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
    @paginate()
    def get_user_events(self, userId: str):
        """
        Retrieves the event history for the specified user.
        """
        user = get_object_or_404(User, id=userId)
        return Events.objects.filter(pgh_context__username=user.username).order_by(
            "-pgh_created_at"
        )
