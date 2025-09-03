import uuid

import pghistory
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Case, Exists, F, OuterRef, Q, When, Min
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import (
    AnnotationGetterMixin,
    AnnotationProperty,
    MappingProperty,
    QueryableProperty,
)


class QueryablePropertiesUserManager(UserManager, QueryablePropertiesManager):
    """
    Custom user manager that combines the functionality of UserManager and QueryablePropertiesManager.

    This manager enables querying user properties using advanced queryable properties features,
    while retaining all standard user management capabilities.

    Inherits:
        UserManager: Provides standard user management operations.
        QueryablePropertiesManager: Adds support for queryable properties on user models.
    """
    pass


class CanManageCasesProperty(AnnotationGetterMixin, QueryableProperty):
    """
    A queryable property that determines whether a user can manage cases.

    This property evaluates several conditions to grant case management permissions:
    - The user is a service account.
    - The user has an access level greater than or equal to 2.
    - The user is a superuser.
    - The user has a valid ProjectDataManagerGrant.

    Returns:
        (bool): Boolean indicating if the user can manage cases.
    """

    def get_annotation(self, cls):
        from onconova.research.models.project import ProjectDataManagerGrant

        return Case(
            When(is_service_account=True, then=True),
            When(
                Q(access_level__gte=2)
                | Q(is_superuser=True)
                | Exists(
                    ProjectDataManagerGrant.objects.filter(
                        member=OuterRef("pk"), is_valid=True
                    )[:1]
                ),
                then=True,
            ),
            default=False,
            output_field=models.BooleanField(),
        )


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser, with additional fields and properties for access control and user metadata.

    Attributes:
        id (models.UUIDField): Primary key, unique identifier for the user.
        full_name (AnnotationProperty): Computed full name from first and last name, or username if missing.
        is_service_account (models.BooleanField): Indicates if the user is a technical service account.
        title (models.CharField): Personal title of the user.
        organization (models.CharField): Organization to which the user belongs.
        department (models.CharField): Department within the organization.
        access_level (models.IntegerField): Numeric access level (0-4) representing user permissions.
        role (MappingProperty): Maps access_level to a human-readable role.
        is_provided (AnnotationProperty): Indicates if the user's identity is provided by an external provider.
        provider (AnnotationProperty): Name of the external provider if applicable.
        can_view_cases (AnnotationProperty): Indicates if the user can view cases (min_access_level=1).
        can_view_projects (AnnotationProperty): Indicates if the user can view projects (min_access_level=1).
        can_view_cohorts (AnnotationProperty): Indicates if the user can view cohorts (min_access_level=1).
        can_view_users (AnnotationProperty): Indicates if the user can view users (min_access_level=1).
        can_view_datasets (AnnotationProperty): Indicates if the user can view datasets (min_access_level=1).
        can_export_data (AnnotationProperty): Indicates if the user can export data (min_access_level=2).
        can_manage_projects (AnnotationProperty): Indicates if the user can manage projects (min_access_level=2).
        can_delete_projects (AnnotationProperty): Indicates if the user can delete projects (min_access_level=3).
        can_delete_cohorts (AnnotationProperty): Indicates if the user can delete cohorts (min_access_level=3).
        can_delete_datasets (AnnotationProperty): Indicates if the user can delete datasets (min_access_level=3).
        can_manage_users (AnnotationProperty): Indicates if the user can manage users (min_access_level=3).
        is_system_admin (AnnotationProperty): Indicates if the user is a system administrator (min_access_level=4).
        can_manage_cases (CanManageCasesProperty): Indicates if the user can manage patient data.

    Methods:
        construct_permission_field_from_access_level(min_access_level, action): Static method to construct permission annotation properties based on access level.
        __str__(): Returns the username as string representation.
        save(*args, **kwargs): Ensures superusers have the highest access level before saving.

    Constraints:
        access_level must be between 0 and 4 (inclusive).
    """

    objects = QueryablePropertiesUserManager()

    class AccessRoles(models.TextChoices):
        """
        Enumeration of access roles within the system.

        Attributes:
            EXTERNAL: Represents an external user with limited access.
            MEMBER: Represents a standard member with regular access.
            PROJECT_MANAGER: Represents a user with project management privileges.
            PLATFORM_MANAGER: Represents a user with platform management privileges.
            SYSTEM_ADMIN: Represents a system administrator with full access.
        """
        EXTERNAL = "External"
        MEMBER = "Member"
        PROJECT_MANAGER = "Project Manager"
        PLATFORM_MANAGER = "Platform Manager"
        SYSTEM_ADMIN = "System Administrator"

    @staticmethod
    def construct_permission_field_from_access_level(min_access_level, action):
        """
        Constructs an annotation property representing a permission field based on the minimum access level and action.

        Args:
            min_access_level (int): The minimum required access level for the permission.
            action (str): The action for which the permission is being checked (e.g., 'edit', 'delete').

        Returns:
            (AnnotationProperty): An annotation property that evaluates to True if the user's access level is greater than or equal to the specified minimum or if the user is a superuser; otherwise, False. The property is annotated with a verbose name describing the action.
        """
        return AnnotationProperty(
            verbose_name=_(f"Can {action}"),
            annotation=Case(
                When(
                    Q(access_level__gte=min_access_level) | Q(is_superuser=True),
                    then=True,
                ),
                default=False,
                output_field=models.BooleanField(),
            ),
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_source = models.CharField(verbose_name="External source", help_text="Name of the source from which the user originated, if imported", max_length=500, null=True, blank=True)
    external_source_id = models.CharField(verbose_name="External source ID", help_text="Unique identifier within the source from which the user originated, if imported", max_length=500, null=True, blank=True)
    full_name = AnnotationProperty(
        verbose_name=_("Full Name"),
        annotation=Case(
            When(
                first_name__isnull=False, 
                last_name__isnull=False, 
                then=Concat(
                    "first_name",
                    models.Value(" "),
                    "last_name",
                    output_field=models.CharField(),
                ),
            ),
            default=F('username'),
            output_field=models.CharField(),
        )
    )
    is_service_account = models.BooleanField(
        verbose_name=_("Is service account?"),
        help_text=_("Whether the user is a technical service account"),
        default=False,
    )
    title = models.CharField(
        verbose_name=_("Title"),
        help_text=_("Personal title of the user"),
        max_length=100,
        blank=True,
        null=True,
    )
    organization = models.CharField(
        verbose_name=_("Organization"),
        help_text=_("Organization to which the user belongs to"),
        max_length=100,
        blank=True,
        null=True,
    )
    department = models.CharField(
        verbose_name=_("Department"),
        help_text=_("Department within an organization to which the user belongs to"),
        max_length=100,
        blank=True,
        null=True,
    )
    access_level = models.IntegerField(
        verbose_name=_("Access level"),
        help_text=_("Level of access of the user in terms of permissions"),
        validators=[MinValueValidator(0), MaxValueValidator(7)],
        default=0,
    )
    shareable = models.BooleanField(
        verbose_name=_("Shareable"),
        help_text=_("Whether user has consented to its data to be shared with other Onconova instances"),
        null=True
    )
    role = MappingProperty(
        verbose_name=_("Role"),
        attribute_path="access_level",
        output_field=models.CharField(choices=AccessRoles),
        mappings=(
            (0, AccessRoles.EXTERNAL),
            (1, AccessRoles.MEMBER),
            (2, AccessRoles.PROJECT_MANAGER),
            (3, AccessRoles.PLATFORM_MANAGER),
            (4, AccessRoles.SYSTEM_ADMIN),
        ),
    )
    is_provided = AnnotationProperty(
        verbose_name=_("Identity provided"),
        annotation=Case(
            When(
                Q(socialaccount__isnull=False)
                & (Q(password__startswith="!") | Q(password__isnull=True)),
                then=True,
            ),
            default=False,
            output_field=models.BooleanField(),
        ),
    )
    provider = AnnotationProperty(
        verbose_name=_("Provider"),
        annotation=Min(
            "socialaccount__provider",
            filter=Q(socialaccount__isnull=False),
            output_field=models.CharField(),
        ),
    )

    # Generated permission fields
    can_view_cases = construct_permission_field_from_access_level(
        min_access_level=1, action="view cases"
    )
    can_view_projects = construct_permission_field_from_access_level(
        min_access_level=1, action="view projects"
    )
    can_view_cohorts = construct_permission_field_from_access_level(
        min_access_level=1, action="view cohorts"
    )
    can_view_users = construct_permission_field_from_access_level(
        min_access_level=1, action="view users"
    )
    can_view_datasets = construct_permission_field_from_access_level(
        min_access_level=1, action="view datasets"
    )
    can_export_data = construct_permission_field_from_access_level(
        min_access_level=2, action="export data"
    )
    can_manage_projects = construct_permission_field_from_access_level(
        min_access_level=2, action="manage projects"
    )
    can_delete_projects = construct_permission_field_from_access_level(
        min_access_level=3, action="delete projects"
    )
    can_delete_cohorts = construct_permission_field_from_access_level(
        min_access_level=3, action="delete cohorts"
    )
    can_delete_datasets = construct_permission_field_from_access_level(
        min_access_level=3, action="delete datasets"
    )
    can_manage_users = construct_permission_field_from_access_level(
        min_access_level=3, action="manage users"
    )
    is_system_admin = construct_permission_field_from_access_level(
        min_access_level=4, action="system admin"
    )
    can_manage_cases = CanManageCasesProperty(
        verbose_name=_("Can manage patient data"),
    )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        """
        Saves the current instance to the database.

        If the user is a superuser, sets the access_level to 4 before saving.
        Calls the parent class's save method to perform the actual save operation.

        Args:
            args (tuple): Variable length argument list.
            kwargs (dict): Arbitrary keyword arguments.
        """
        if self.is_superuser:
            self.access_level = 4
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(access_level__gte=0) & Q(access_level__lte=4),
                name="access_level_must_be_between_0_and_4",
            )
        ]
