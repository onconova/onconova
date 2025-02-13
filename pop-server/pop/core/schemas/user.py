from ninja import Field, Schema
from pop.core import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class UserPermissions(Schema):
    canViewCases: bool = Field(alias='can_view_cases')
    canViewProjects: bool = Field(alias='can_view_projects')
    canViewCohorts: bool = Field(alias='can_view_cohorts')
    canViewUsers: bool = Field(alias='can_view_users')
    canImportData: bool = Field(alias='can_import_data')
    canManageCases: bool = Field(alias='can_manage_cases')
    canManageCohorts: bool = Field(alias='can_manage_cohorts')
    canAnalyzeData: bool = Field(alias='can_analyze_data')
    canExportData: bool = Field(alias='can_export_data')
    canManageProjects: bool = Field(alias='can_manage_projects')
    canAccessSensitive_data: bool = Field(alias='can_access_sensitive_data')
    canAuditLogs: bool = Field(alias='can_audit_logs')
    canManageUsers: bool = Field(alias='can_manage_users')
    isSystemAdmin: bool = Field(alias='is_system_admin')

class UserSchema(ModelGetSchema):
    role: orm.User.AccessRoles = Field(description='User role based on its access level')
    permissions: UserPermissions = Field(description='User permissions based on access level')
    config = SchemaConfig(model=orm.User, exclude=['date_joined', 'groups', 'is_staff', 'is_superuser', 'user_permissions'])    

class UserCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.User, exclude=['date_joined', 'groups', 'is_staff', 'is_superuser', 'user_permissions'])    

class UserProfileSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.User, fields=['first_name', 'last_name', 'organization', 'title', 'department'])    
