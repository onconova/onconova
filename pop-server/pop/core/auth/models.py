import uuid 
import pghistory
from django.db import models
from django.db.models import Case, When, Q, Min, Exists, OuterRef
from django.db.models.functions import Concat
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, UserManager

from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import AnnotationProperty, MappingProperty, AnnotationGetterMixin, QueryableProperty

class QueryablePropertiesUserManager(UserManager, QueryablePropertiesManager):
    pass


class CanManageCasesProperty(AnnotationGetterMixin, QueryableProperty):

    def get_annotation(self, cls):
        from pop.research.models.project import ProjectDataManagerGrant
        return Case(
            When(
                Q(access_level__gte=4) 
                | Q(is_superuser=True) 
                | Exists(ProjectDataManagerGrant.objects.filter(member=OuterRef('pk'), is_valid=True)[:1]), 
                then=True
            ), 
            default=False, 
            output_field=models.BooleanField(),
        )

class User(AbstractUser):
    
    objects = QueryablePropertiesUserManager()

    class AccessRoles(models.TextChoices):
        EXTERNAL = 'External'
        VIEWER = 'Viewer'
        DATA_CONTRIBUTOR = 'Data Contributor'
        DATA_ANALYST = 'Data Analyst'
        PROJECT_MANAGER = 'Project Manager'
        PLATFORM_MANAGER = 'Platform Manager'
        SYSTEM_ADMIN = 'System Administrator'
        
    def construct_permission_field_from_access_level(min_access_level, action):
        return AnnotationProperty(
            verbose_name = _(f'Can {action}'),
            annotation = Case(When(Q(access_level__gte=min_access_level) | Q(is_superuser=True), then=True), default=False, output_field=models.BooleanField()),
        )
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    full_name = AnnotationProperty(
        verbose_name = _('Full Name'),
        annotation = Concat('first_name', models.Value(' '), 'last_name', output_field=models.CharField()),
    )
    title = models.CharField(
        verbose_name = _('Title'),
        help_text = _('Personal title of the user'),
        max_length = 100, 
        blank = True, 
        null = True
    )
    organization = models.CharField(
        verbose_name = _('Organization'),
        help_text = _('Organization to which the user belongs to'),
        max_length = 100, 
        blank = True, 
        null = True
    )
    department = models.CharField(
        verbose_name = _('Department'),
        help_text = _('Department within an organization to which the user belongs to'),
        max_length = 100, 
        blank = True, 
        null = True
    )
    access_level = models.IntegerField(
        verbose_name = _('Access level'),
        help_text = _('Level of access of the user in terms of permissions'),
        validators = [MinValueValidator(0), MaxValueValidator(7)],        
        default=0,
    )
    role = MappingProperty(
        verbose_name = _('Role'),
        attribute_path = 'access_level',
        output_field = models.CharField(choices=AccessRoles),
        mappings= (
            (0, AccessRoles.EXTERNAL),
            (1, AccessRoles.VIEWER),
            (2, AccessRoles.DATA_CONTRIBUTOR),
            (3, AccessRoles.DATA_ANALYST),
            (4, AccessRoles.PROJECT_MANAGER),
            (5, AccessRoles.PLATFORM_MANAGER),
            (6, AccessRoles.SYSTEM_ADMIN),
        )
    )    
    is_provided = AnnotationProperty(
        verbose_name = _('Identity provided'),
        annotation = Case(
            When(Q(socialaccount__isnull=False) & (Q(password__startswith='!') | Q(password__isnull=True)), then=True), 
            default=False, output_field=models.BooleanField()),
    )
    provider = AnnotationProperty(
        verbose_name = _('Provider'),
        annotation = Min('socialaccount__provider', filter=Q(socialaccount__isnull=False), output_field=models.CharField()),
    )

    # Generated permission fields
    can_view_cases = construct_permission_field_from_access_level(
        min_access_level = 1, 
        action = 'view cases'
    )
    can_view_projects = construct_permission_field_from_access_level(
        min_access_level = 1, 
        action = 'view projects'
    )
    can_view_cohorts = construct_permission_field_from_access_level(
        min_access_level = 1, 
        action = 'view cohorts'
    )
    can_view_users = construct_permission_field_from_access_level(
        min_access_level = 1, 
        action = 'view users'
    )
    can_view_datasets = construct_permission_field_from_access_level(
        min_access_level = 1, action = 'view datasets'
    )
    can_import_data = construct_permission_field_from_access_level(
        min_access_level = 2, 
        action = 'import data'
    )
    can_manage_cohorts = construct_permission_field_from_access_level(
        min_access_level = 2, 
        action = 'manage cohorts'
    )
    can_manage_datasets = construct_permission_field_from_access_level(
        min_access_level = 2, 
        action = 'manage datasets'
    )
    can_analyze_data = construct_permission_field_from_access_level(
        min_access_level = 3, 
        action = 'analyze data'
    )
    can_export_data = construct_permission_field_from_access_level(
        min_access_level = 3, 
        action = 'export data'
    )
    can_manage_projects = construct_permission_field_from_access_level(
        min_access_level = 4, 
        action = 'manage projects'
    )
    can_access_sensitive_data = construct_permission_field_from_access_level(
        min_access_level = 4, 
        action = 'access sensitive data'
    )
    can_delete_projects = construct_permission_field_from_access_level(
        min_access_level = 5, 
        action = 'delete projects'
    )
    can_audit_logs = construct_permission_field_from_access_level( 
        min_access_level = 5,
        action='audit logs'
    )
    can_manage_users = construct_permission_field_from_access_level(
        min_access_level = 5, 
        action = 'manage users'
    )
    is_system_admin = construct_permission_field_from_access_level(
        min_access_level = 6, 
        action = 'system admin'
    )
    can_manage_cases = CanManageCasesProperty(
        verbose_name = _('Can manage cases data'),
    )

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.access_level = 6
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(access_level__gte=0) & Q(access_level__lte=6),
                name="access_level_must_be_between_1_and_6",
            )
        ]