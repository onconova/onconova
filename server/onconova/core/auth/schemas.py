"""
This module defines Pydantic schemas for user authentication and profile management within the Onconova system.
"""
from typing import Literal
from ninja import Field, Schema
from datetime import datetime

from onconova.core.serialization.factory import create_filters_schema
from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, MetadataMixin, AnonymizationMixin
from onconova.core.types import Nullable, UUID
from onconova.core.auth import models as orm


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


class UserCreate(BaseSchema):
    
    __orm_model__ = orm.User #type: ignore
    
    lastLogin: Nullable[datetime] = Field(
        None, description='', 
        title='Last Login',
    )
    username: str = Field(
        ...,
        description='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        title='Username',
        max_length=150,
    )
    firstName: Nullable[str] = Field(
        None, description='', title='First Name',
        max_length=150,
    )
    lastName: Nullable[str] = Field(
        None, description='', title='Last Name',
        max_length=150,
    )
    email: Nullable[str] = Field(
        None, description='', title='Email Address',
        max_length=254,
    )
    isActive: bool = Field(
        True,
        description='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
        title='Active',
    )
    externalSource: Nullable[str] = Field(
        None,
        description='Name of the source from which the user originated, if imported',
        title='External source',
        max_length=500,
    )
    externalSourceId: Nullable[str] = Field(
        None,
        description='Unique identifier within the source from which the user originated, if imported',
        title='External source ID',
        max_length=500,
    )
    isServiceAccount: bool = Field(
        False,
        description='Whether the user is a technical service account',
        title='Is service account?',
    )
    title: Nullable[str] = Field(
        None, 
        description='Personal title of the user', 
        title='Title',
        max_length=100,
    )
    organization: Nullable[str] = Field(
        None,
        description='Organization to which the user belongs to',
        title='Organization',
        max_length=100,
    )
    department: Nullable[str] = Field(
        None,
        description='Department within an organization to which the user belongs to',
        title='Department',
        max_length=100,
    )
    accessLevel: int = Field(
        0,
        description='Level of access of the user in terms of permissions',
        title='Access level',
    )
    shareable: Nullable[bool] = Field(
        None,
        description='Whether user has consented to its data to be shared with other Onconova instances',
        title='Shareable',
    )


class User(UserCreate):

    id: UUID = Field(
        ..., 
        description='Unique identifier of the resource (UUID v4).', 
        title='Id'
    )
    fullName: str = Field(
        title="Full Name",
        description="The user's full name.",
    )
    role: orm.User.AccessRoles = Field(
        title="Role", description="The user's assigned access role."
    )
    canViewCases: bool = Field(
        title="View Cases",
        description="Permission to view cases.",
    )
    canViewProjects: bool = Field(
        title="View Projects",
        description="Permission to view projects.",
    )
    canViewCohorts: bool = Field(
        title="View Cohorts",
        description="Permission to view cohorts.",
    )
    canViewUsers: bool = Field(
        title="View Users",
        description="Permission to view other user accounts.",
    )
    canViewDatasets: bool = Field(
        title="View Datasets",
        description="Permission to view available datasets.",
    )
    canManageCases: bool = Field(
        title="Manage Cases",
        description="Permission to manage cases.",
    )
    canExportData: bool = Field(
        title="Export Data",
        description="Permission to export data out of the system.",
    )
    canManageProjects: bool = Field(
        title="Manage Projects",
        description="Permission to manage projects.",
    )
    canManageUsers: bool = Field(
        title="Manage Users",
        description="Permission to create and manage users.",
    )
    isSystemAdmin: bool = Field(
        title="System Administrator",
        description="Whether the user is a system administrator.",
    )
    isProvided: bool = Field(
        title="Is Provided",
        description="Indicates whether the user account is externally provided.",
    )
    provider: Nullable[str] = Field(
        default=None,
        title="Provider",
        description="The external authentication provider, if applicable.",
    )
    

class UserExport(BaseSchema, AnonymizationMixin):
    """User information to be exported for acreditation purposes"""
    
    __orm_model__ = orm.User # type: ignore 
    
    id: UUID = Field(
        ..., 
        description='Unique identifier of the resource (UUID v4).', 
        title='Id'
    )
    externalSource: Nullable[str] = Field(
        None,
        description='Name of the source from which the user originated, if imported',
        title='External source',
        max_length=500,
    )
    externalSourceId: Nullable[str] = Field(
        None,
        description='Unique identifier within the source from which the user originated, if imported',
        title='External source ID',
        max_length=500,
    )
    username: str = Field(
        ...,
        description='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        title='Username',
        max_length=150,
    )
    firstName: Nullable[str] = Field(
        default=None,
        title="First Name",
        description="The user's given name.",
        max_length=150,
    )
    lastName: Nullable[str] = Field(
        default=None,
        title="Last Name",
        description="The user's surname.",
        max_length=150,
    )
    organization: Nullable[str] = Field(
        default=None,
        title="Organization",
        description="The user's affiliated organization.",
        max_length=100,
    )
    email: Nullable[str] = Field(
        default=None,
        title="Email Address", 
        description="The user's primary email address.",        
        max_length=254,
    )
    
    @staticmethod 
    def resolve_anonymized(user):
        return not user.shareable
    
    

class UserProfile(BaseSchema):
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
    )
    lastName: Nullable[str] = Field(
        title="Last Name",
        description="The user's surname.",
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


UserFilters = create_filters_schema(schema=User, name="UserFilters")
"""Dynamically generated schema for filtering users, based on User schema."""



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


class AuthenticationMeta(BaseSchema):
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
    )
    accessToken: Nullable[str] = Field(
        default=None,
        title="Access Token",
        description="The access token for the authenticated session, if available.",
    )
    isAuthenticated: bool = Field(
        title="Is Authenticated",
        description="Indicates whether the user is authenticated.",
    )