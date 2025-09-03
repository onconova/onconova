"""
This module defines Pydantic schemas for user authentication and profile management within the Onconova system.
"""
from ninja import Field, Schema
from typing import Literal
from pydantic import AliasChoices, model_validator, PrivateAttr
from onconova.core.auth import models as orm
from onconova.core.serialization.factory import create_filters_schema
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.core.types import Nullable


class UserPasswordReset(Schema):
    """
    Schema for user password reset operation.

    Attributes:
        oldPassword (str): The user's current password.
        newPassword (str): The user's new password to be set.
    """

    oldPassword: str = Field(
        title="Old Password", description="The user's current password."
    )
    newPassword: str = Field(
        title="New Password", description="The user's new password to be set."
    )


class UserExportSchema(ModelGetSchema):
    """User information to be exported for acreditation purposes"""
    
    anonymized: bool = Field(
        title='Anonymzied',
        default=True      
    )
    config = SchemaConfig(
        model=orm.User,
        fields=[
            "id",
            "external_source",
            "external_source_id",
            "username",
            "first_name",
            "last_name",
            "email",
            "organization",
        ],
    )
    

class UserSchema(ModelGetSchema):
    """
    Schema for representing a user and their permissions within the system.

    Attributes:
        role (orm.User.AccessRoles): The user's assigned access role.
        canViewCases (bool): Permission to view cases.
        canViewProjects (bool): Permission to view projects.
        canViewCohorts (bool): Permission to view cohorts.
        canViewUsers (bool): Permission to view other user accounts.
        canViewDatasets (bool): Permission to view available datasets.
        canManageCases (bool): Permission to manage cases.
        canExportData (bool): Permission to export data out of the system.
        canManageProjects (bool): Permission to manage projects.
        canManageUsers (bool): Permission to create and manage users.
        isSystemAdmin (bool): Whether the user is a system administrator.
        isProvided (bool): Indicates whether the user account is externally provided.
        provider (Optional[str]): The external authentication provider, if applicable.

    Config:
        Associated to the `onconova.core.models.User` ORM model to autogenerate fields for this schema.
    """

    fullName: str = Field(
        title="Full Name",
        description="The user's full name.",
        alias="full_name",
        validation_alias=AliasChoices("fullName", "full_name"),
    )
    role: orm.User.AccessRoles = Field(
        title="Role", description="The user's assigned access role."
    )
    canViewCases: bool = Field(
        title="View Cases",
        description="Permission to view cases.",
        alias="can_view_cases",
        validation_alias=AliasChoices("canViewCases", "can_view_cases"),
    )
    canViewProjects: bool = Field(
        title="View Projects",
        description="Permission to view projects.",
        alias="can_view_projects",
        validation_alias=AliasChoices("canViewProjects", "can_view_projects"),
    )
    canViewCohorts: bool = Field(
        title="View Cohorts",
        description="Permission to view cohorts.",
        alias="can_view_cohorts",
        validation_alias=AliasChoices("canViewCohorts", "can_view_cohorts"),
    )
    canViewUsers: bool = Field(
        title="View Users",
        description="Permission to view other user accounts.",
        alias="can_view_users",
        validation_alias=AliasChoices("canViewUsers", "can_view_users"),
    )
    canViewDatasets: bool = Field(
        title="View Datasets",
        description="Permission to view available datasets.",
        alias="can_view_datasets",
        validation_alias=AliasChoices("canViewDatasets", "can_view_datasets"),
    )
    canManageCases: bool = Field(
        title="Manage Cases",
        description="Permission to manage cases.",
        alias="can_manage_cases",
        validation_alias=AliasChoices("canManageCases", "can_manage_cases"),
    )
    canExportData: bool = Field(
        title="Export Data",
        description="Permission to export data out of the system.",
        alias="can_export_data",
        validation_alias=AliasChoices("canExportData", "can_export_data"),
    )
    canManageProjects: bool = Field(
        title="Manage Projects",
        description="Permission to manage projects.",
        alias="can_manage_projects",
        validation_alias=AliasChoices("canManageProjects", "can_manage_projects"),
    )
    canManageUsers: bool = Field(
        title="Manage Users",
        description="Permission to create and manage users.",
        alias="can_manage_users",
        validation_alias=AliasChoices("canManageUsers", "can_manage_users"),
    )
    isSystemAdmin: bool = Field(
        title="System Administrator",
        description="Whether the user is a system administrator.",
        alias="is_system_admin",
        validation_alias=AliasChoices("isSystemAdmin", "is_system_admin"),
    )
    isProvided: bool = Field(
        title="Is Provided",
        description="Indicates whether the user account is externally provided.",
        alias="is_provided",
        validation_alias=AliasChoices("isProvided", "is_provided"),
    )
    provider: Nullable[str] = Field(
        default=None,
        title="Provider",
        description="The external authentication provider, if applicable.",
        alias="provider",
        validation_alias=AliasChoices("provider", "provider"),
    )

    config = SchemaConfig(
        model=orm.User,
        exclude=[
            "date_joined",
            "groups",
            "is_staff",
            "is_superuser",
            "user_permissions",
            "password",
        ],
    )


class UserCreateSchema(ModelCreateSchema):
    """
    Schema for creating a new User instance.

    Config:
        Associated to the `onconova.core.models.User` ORM model to autogenerate fields for this schema.
    """

    config = SchemaConfig(
        model=orm.User,
        exclude=[
            "id",
            "date_joined",
            "groups",
            "is_staff",
            "is_superuser",
            "user_permissions",
            "password",
        ],
    )


class UserProfileSchema(Schema):
    """
    Schema representing a user's profile information.

    Attributes:
        firstName (Optional[str]): The user's given name. Accepts either 'firstName' or 'first_name' as input.
        lastName (Optional[str]): The user's surname. Accepts either 'lastName' or 'last_name' as input.
        organization (Optional[str]): The user's affiliated organization.
        department (Optional[str]): The user's department within the organization.
        title (Optional[str]): The user's job title or position.
        email (str): The user's primary email address.
    """

    firstName: Nullable[str] = Field(
        title="First Name",
        description="The user's given name.",
        alias="first_name",
        validation_alias=AliasChoices("firstName", "first_name"),
    )
    lastName: Nullable[str] = Field(
        title="Last Name",
        description="The user's surname.",
        alias="last_name",
        validation_alias=AliasChoices("lastName", "last_name"),
    )
    organization: Nullable[str] = Field(
        default=None,
        title="Organization",
        description="The user's affiliated organization.",
    )
    department: Nullable[str] = Field(
        default=None,
        title="Department",
        description="The user's department within the organization.",
    )
    title: Nullable[str] = Field(
        default=None, title="Job Title", description="The user's job title or position."
    )
    email: str = Field(
        title="Email Address", description="The user's primary email address."
    )


UserFilters = create_filters_schema(schema=UserSchema, name="UserFilters")
"""Dynamically generated schema for filtering users, based on UserSchema."""



class UserCredentials(Schema):
    """
    Schema representing user credentials required for authentication.

    Attributes:
        username (str): The username of the user.
        password (str): The password associated with the username.
    """
    username: str = Field(
        title="Username",
        description="The username of the user."
    )
    password: str = Field(
        title="Password",
        description="The password associated with the username."
    )


class UserProviderClientToken(Schema):
    """
    Schema representing a user's authentication tokens provided by a client.

    Attributes:
        client_id (str): The unique identifier for the client application.
        id_token (Optional[str]): The ID token issued by the authentication provider, if available.
        access_token (Optional[str]): The access token issued by the authentication provider, if available.
    """
    client_id: str = Field(
        title="Client ID",
        description="The unique identifier for the client application."
    )
    id_token: Nullable[str] = Field(
        default=None,
        title="ID Token",
        description="The ID token issued by the authentication provider, if available."
    )
    access_token: Nullable[str] = Field(
        default=None,
        title="Access Token",
        description="The access token issued by the authentication provider, if available."
    )


class UserProviderToken(Schema):
    """
    Schema representing a user's provider token information.

    Attributes:
        provider (str): The name of the authentication provider (e.g., 'google', 'facebook').
        process (Literal["login"] | Literal["connect"]): The process type, either 'login' or 'connect'.
        token (UserProviderClientToken): The token object containing provider-specific authentication details.
    """
    provider: str = Field(
        title="Provider",
        description="The name of the authentication provider (e.g., 'google', 'facebook')."
    )
    process: Literal["login"] | Literal["connect"] = Field(
        title="Process Type",
        description="The process type, either 'login' or 'connect'."
    )
    token: UserProviderClientToken = Field(
        title="Provider Token",
        description="The token object containing provider-specific authentication details."
    )


class AuthenticationMeta(Schema):
    """
    Schema representing authentication metadata.

    Attributes:
        sessionToken (Optional[str]): The session token associated with the authentication, if available.
        accessToken (Optional[str]): The access token for the authenticated session, if available.
        isAuthenticated (bool): Indicates whether the user is authenticated.
    """
    sessionToken: Nullable[str] = Field(
        default=None,
        title="Session Token",
        description="The session token associated with the authentication, if available.",
        alias="session_token",
        validation_alias=AliasChoices("sessionToken", "session_token"),
    )
    accessToken: Nullable[str] = Field(
        default=None,
        title="Access Token",
        description="The access token for the authenticated session, if available.",
        alias="access_token",
        validation_alias=AliasChoices("accessToken", "access_token"),
    )
    isAuthenticated: bool = Field(
        title="Is Authenticated",
        description="Indicates whether the user is authenticated.",
        alias="is_authenticated",
        validation_alias=AliasChoices("isAuthenticated", "is_authenticated"),
    )