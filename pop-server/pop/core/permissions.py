from ninja_extra import permissions, api_controller, http_get
from django.db import models 
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from pop.core.models import User

class BasePermission(permissions.BasePermission):
    
    def check_user_permission(self, user: User):
        raise NotImplementedError 
    
    def has_permission(self, request: HttpRequest, controller):
        return request.user.is_superuser or (not isinstance(request.user, AnonymousUser) and (request.user.is_system_admin or self.check_user_permission(request.user)))


class CanViewUsers(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_view_users


class CanViewCases(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_view_cases


class CanViewCohorts(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_view_cohorts


class CanViewProjects(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_view_projects


class CanManageCases(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_manage_cases    


class CanManageCohorts(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_manage_cohorts  


class CanExportData(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_export_data 


class CanManageProjects(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_manage_projects


class CanAccessSensitiveData(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_access_sensitive_data


class CanAuditLogs(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_audit_logs


class CanManageUsers(BasePermission):
    def check_user_permission(self, user: User):
        return user.can_manage_users

class IsRequestingUser(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, controller):
        # Access route context and compute parameters
        controller.context.compute_route_parameters()
        userId = controller.context.kwargs.get('userId')
        return request.user.id == userId