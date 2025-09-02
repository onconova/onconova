from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.http import HttpRequest
from ninja_extra import permissions
from typing import Any
from onconova.core.auth.models import User
from onconova.research.models.cohort import Cohort
from onconova.research.models.dataset import Dataset
from onconova.research.models.project import Project


class BasePermission(permissions.BasePermission):
    """
    Base permission class providing common permission evaluation logic.
    """

    def check_user_permission(self, user: User) -> bool:
        """
        Checks whether the given user has the required permission.

        Args:
            user (User): The user object whose permissions are to be checked.

        Returns:
            (bool): True if the user has the required permission, False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement check_user_permission.")

    def check_user_object_permission(self, user: User, controller: Any, obj: object) -> bool:
        """
        Checks whether the given user has permission to access or perform actions on the specified object.

        Args:
            user (User): The user whose permissions are being checked.
            controller (Any): The controller or context in which the permission is being checked.
            obj (object): The object for which permission is being evaluated.

        Returns:
            (bool): True if the user has permission for the object, False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(
            "Subclasses must implement check_user_object_permission."
        )

    def has_permission(self, request: HttpRequest, controller: Any) -> bool:
        """
        Determines whether the requesting user has permission to access the controller.

        Args:
            request (HttpRequest): The HTTP request containing the user information.
            controller (Any): The controller or view being accessed.

        Returns:
            (bool): True if the user is a superuser, a system admin, or passes the custom user permission check; False otherwise.
        """
        user = request.user
        return user.is_superuser or (
            not isinstance(user, AnonymousUser)
            and (user.is_system_admin or self.check_user_permission(user))
        )

    def has_object_permission(self, request: HttpRequest, controller: Any, obj: object) -> bool:
        """
        Determines whether the requesting user has permission to access a specific object.

        Args:
            request (HttpRequest): The HTTP request containing the user information.
            controller (Any): The controller handling the request (usage may vary).
            obj (object): The object for which permission is being checked.

        Returns:
            (bool): True if the user is a superuser, a system admin, or passes the custom object permission check;
                  False otherwise.
        """
        user = request.user
        return user.is_superuser or (
            not isinstance(user, AnonymousUser)
            and (
                user.is_system_admin
                or self.check_user_object_permission(user, controller, obj)
            )
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


class CanManageCohorts(BasePermission):
    """Permission to manage cohorts."""

    def check_user_permission(self, user: User) -> bool:
        return user.access_level > 2 or (
            user.access_level > 0
            and Project.objects.filter(Q(members=user) | Q(leader=user)).exists()
        )

    def check_user_object_permission(self, user, _, cohort: Cohort):
        # Elevated roles can manage any project
        if user.role in (
            User.AccessRoles.PLATFORM_MANAGER,
            User.AccessRoles.SYSTEM_ADMIN,
        ):
            return True
        elif user.role in (
            User.AccessRoles.PROJECT_MANAGER,
            User.AccessRoles.MEMBER,
        ):
            # Project managers can only manage their own project
            return cohort.project.is_member(user)
        else:
            return False


class CanManageProjects(BasePermission):
    """Permission to manage projects."""

    def check_user_permission(self, user: User) -> bool:
        return user.can_manage_projects

    def check_user_object_permission(self, user, _, project: Project):
        print("CHECKING PROJECT ROLE: ", user.role)
        # Elevated roles can manage any project
        if user.role in (
            User.AccessRoles.PLATFORM_MANAGER,
            User.AccessRoles.SYSTEM_ADMIN,
        ):
            return True
        elif user.role == User.AccessRoles.PROJECT_MANAGER:
            # Project managers can only manage their own project
            return user == project.leader
        else:
            return False


class CanManageDatasets(BasePermission):
    """Permission to manage datasets."""

    def check_user_permission(self, user: User) -> bool:
        return user.access_level > 2 or (
            user.access_level > 0
            and Project.objects.filter(Q(members=user) | Q(leader=user)).exists()
        )

    def check_user_object_permission(self, user, _, dataset: Dataset):
        # Elevated roles can manage any project
        if user.role in (
            User.AccessRoles.PLATFORM_MANAGER,
            User.AccessRoles.SYSTEM_ADMIN,
        ):
            return True
        elif user.role in (
            User.AccessRoles.PROJECT_MANAGER,
            User.AccessRoles.MEMBER,
        ):
            # Project managers can only manage their own project
            return dataset.project.is_member(user)
        else:
            return False


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


class CanDeleteCohorts(BasePermission):
    """Permission to delete cohorts."""

    def check_user_permission(self, user: User) -> bool:
        return user.can_delete_cohorts


class CanDeleteDatasets(BasePermission):
    """Permission to delete datasets."""

    def check_user_permission(self, user: User) -> bool:
        return user.can_delete_datasets


class IsRequestingUser(permissions.BasePermission):
    """
    Permission that grants access only if the user making the request
    matches the `userId` parameter in the URL route.
    """

    def has_permission(self, request: HttpRequest, controller: Any) -> bool:
        """
        Check if the authenticated user's ID matches the `userId` in the route.

        Args:
            request (HttpRequest): Incoming HTTP request.
            controller (Any): The view/controller handling the request.

        Returns:
            (bool): Whether permission is granted.
        """
        controller.context.compute_route_parameters()
        user_id = controller.context.kwargs.get("userId")
        return str(request.user.id) == str(user_id)
