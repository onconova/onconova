from ninja_extra import permissions
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from pop.core.auth.models import User

class BasePermission(permissions.BasePermission):
    """
    Base permission class providing common permission evaluation logic.

    Permissions are granted if:
    - The user is a superuser
    - The user is a system admin
    - The user passes a specific permission check (defined in subclasses)
    """

    def check_user_permission(self, user: User) -> bool:
        """
        Check if a user has a specific permission.

        Subclasses must override this method.

        Args:
            user (User): The user object.

        Returns:
            bool: Whether the user has the required permission.
        """
        raise NotImplementedError("Subclasses must implement check_user_permission.")

    def has_permission(self, request: HttpRequest, controller) -> bool:
        """
        Evaluate whether a request has permission to proceed.

        Args:
            request (HttpRequest): Incoming HTTP request.
            controller: The view/controller handling the request.

        Returns:
            bool: Whether permission is granted.
        """
        user = request.user
        return (
            user.is_superuser
            or (not isinstance(user, AnonymousUser)
                and (user.is_system_admin or self.check_user_permission(user)))
        )


# View permissions
class CanViewUsers(BasePermission):
    """Permission to view user accounts."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_view_users


class CanViewCases(BasePermission):
    """Permission to view cases."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_view_cases


class CanViewCohorts(BasePermission):
    """Permission to view cohorts."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_view_cohorts


class CanViewDatasets(BasePermission):
    """Permission to view datasets."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_view_datasets


class CanViewProjects(BasePermission):
    """Permission to view projects."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_view_projects


# Manage permissions
class CanManageCases(BasePermission):
    """Permission to manage cases."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_manage_cases


class CanManageDatasets(BasePermission):
    """Permission to manage datasets."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_manage_datasets


class CanManageCohorts(BasePermission):
    """Permission to manage cohorts."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_manage_cohorts


class CanManageProjects(BasePermission):
    """Permission to manage projects."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_manage_projects


class CanManageUsers(BasePermission):
    """Permission to manage users."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_manage_users


# Other permissions
class CanExportData(BasePermission):
    """Permission to export data."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_export_data


class CanDeleteProjects(BasePermission):
    """Permission to delete projects."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_delete_projects


class CanAccessSensitiveData(BasePermission):
    """Permission to access sensitive data."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_access_sensitive_data


class CanAuditLogs(BasePermission):
    """Permission to view audit logs."""
    def check_user_permission(self, user: User) -> bool:
        return user.can_audit_logs


class IsRequestingUser(permissions.BasePermission):
    """
    Permission that grants access only if the user making the request
    matches the 'userId' parameter in the URL route.
    """

    def has_permission(self, request: HttpRequest, controller) -> bool:
        """
        Check if the authenticated user's ID matches the 'userId' in the route.

        Args:
            request (HttpRequest): Incoming HTTP request.
            controller: The view/controller handling the request.

        Returns:
            bool: Whether permission is granted.
        """
        controller.context.compute_route_parameters()
        user_id = controller.context.kwargs.get("userId")
        return str(request.user.id) == str(user_id)