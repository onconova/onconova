from typing import Optional
from ninja import Field, Schema
from pydantic import AliasChoices
from pop.core import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig, BaseSchema
from pydantic import SecretStr

class UserPasswordReset(Schema):
    oldPassword: str 
    newPassword: str

class UserSchema(ModelGetSchema):
    role: orm.User.AccessRoles = Field(description='User role based on its access level')
    canViewCases: bool = Field(alias='can_view_cases', validation_alias=AliasChoices('canViewCases', 'can_view_cases'))
    canViewProjects: bool = Field(alias='can_view_projects', validation_alias=AliasChoices('canViewProjects', 'can_view_projects'))
    canViewCohorts: bool = Field(alias='can_view_cohorts', validation_alias=AliasChoices('canViewCohorts', 'can_view_cohorts'))
    canViewUsers: bool = Field(alias='can_view_users', validation_alias=AliasChoices('canViewUsers', 'can_view_users'))
    canViewDatasets: bool = Field(alias='can_view_datasets', validation_alias=AliasChoices('canViewDatasets', 'can_view_datasets'))
    canImportData: bool = Field(alias='can_import_data', validation_alias=AliasChoices('canImportData', 'can_import_data'))
    canManageCases: bool = Field(alias='can_manage_cases', validation_alias=AliasChoices('canManageCases', 'can_manage_cases'))
    canManageCohorts: bool = Field(alias='can_manage_cohorts', validation_alias=AliasChoices('canManageCohorts', 'can_manage_cohorts'))
    canManageDatasets: bool = Field(alias='can_manage_datasets', validation_alias=AliasChoices('canManageDatasets', 'can_manage_datasets'))
    canAnalyzeData: bool = Field(alias='can_analyze_data', validation_alias=AliasChoices('canAnalyzeData', 'can_analyze_data'))
    canExportData: bool = Field(alias='can_export_data', validation_alias=AliasChoices('canExportData', 'can_export_data'))
    canManageProjects: bool = Field(alias='can_manage_projects', validation_alias=AliasChoices('canManageProjects', 'can_manage_projects'))
    canAccessSensitiveData: bool = Field(alias='can_access_sensitive_data', validation_alias=AliasChoices('canAccessSensitiveData', 'can_access_sensitive_data'))
    canAuditLogs: bool = Field(alias='can_audit_logs', validation_alias=AliasChoices('canAuditLogs', 'can_audit_logs'))
    canManageUsers: bool = Field(alias='can_manage_users', validation_alias=AliasChoices('canManageUsers', 'can_manage_users'))
    isSystemAdmin: bool = Field(alias='is_system_admin', validation_alias=AliasChoices('isSystemAdmin', 'is_system_admin'))
    config = SchemaConfig(model=orm.User, exclude=['date_joined', 'groups', 'is_staff', 'is_superuser', 'user_permissions', 'password'])    

class UserCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.User, exclude=['id','date_joined', 'groups', 'is_staff', 'is_superuser', 'user_permissions', 'password'])    

class UserProfileSchema(Schema):
    firstName: Optional[str] = Field(alias='first_name', validation_alias=AliasChoices('firstName', 'first_name'))
    lastName: Optional[str] = Field(alias='last_name', validation_alias=AliasChoices('lastName', 'last_name')) 
    organization: Optional[str] = None 
    department: Optional[str] = None     
    title: Optional[str] = None 
    email: str 
