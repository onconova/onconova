import uuid

import pghistory
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Case, Exists, Min, OuterRef, Q, When
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
    pass


class CanManageCasesProperty(AnnotationGetterMixin, QueryableProperty):

    def get_annotation(self, cls):
        from pop.research.models.project import ProjectDataManagerGrant

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

    objects = QueryablePropertiesUserManager()

    class AccessRoles(models.TextChoices):
        EXTERNAL = "External"
        MEMBER = "Member"
        PROJECT_MANAGER = "Project Manager"
        PLATFORM_MANAGER = "Platform Manager"
        SYSTEM_ADMIN = "System Administrator"

    @staticmethod
    def construct_permission_field_from_access_level(min_access_level, action):
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
    full_name = AnnotationProperty(
        verbose_name=_("Full Name"),
        annotation=Concat(
            "first_name",
            models.Value(" "),
            "last_name",
            output_field=models.CharField(),
        ),
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
