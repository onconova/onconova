from typing import Optional

from ninja import Field, Schema
from pydantic import AliasChoices

from pop.core.auth import models as orm
from pop.core.serialization.metaclasses import (
    ModelGetSchema,
    ModelCreateSchema,
    SchemaConfig,
)
from pop.core.serialization.factory import create_filters_schema


class UserPasswordReset(Schema):
    """Schema for user password reset payload."""

    oldPassword: str = Field(
        title="Old Password", description="The user's current password."
    )
    newPassword: str = Field(
        title="New Password", description="The user's new password to be set."
    )


class UserSchema(ModelGetSchema):
    """Detailed schema for User data retrieval."""

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
    provider: Optional[str] = Field(
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
    """Schema for creating a new user."""

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
    """Schema for user profile data."""

    firstName: Optional[str] = Field(
        title="First Name",
        description="The user's given name.",
        alias="first_name",
        validation_alias=AliasChoices("firstName", "first_name"),
    )
    lastName: Optional[str] = Field(
        title="Last Name",
        description="The user's surname.",
        alias="last_name",
        validation_alias=AliasChoices("lastName", "last_name"),
    )
    organization: Optional[str] = Field(
        default=None,
        title="Organization",
        description="The user's affiliated organization.",
    )
    department: Optional[str] = Field(
        default=None,
        title="Department",
        description="The user's department within the organization.",
    )
    title: Optional[str] = Field(
        default=None, title="Job Title", description="The user's job title or position."
    )
    email: str = Field(
        title="Email Address", description="The user's primary email address."
    )


# Filters
UserFilters = create_filters_schema(schema=UserSchema, name="UserFilters")
