import uuid 
import pghistory
from django.db import models
from django.db.models import Case, When, Q
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from queryable_properties.properties import MappingProperty
from queryable_properties.properties import AnnotationProperty


class User(AbstractUser):
        
    class AccessRoles(models.TextChoices):
        EXTERNAL = 'External'
        VIEWER = 'Viewer'
        DATA_CONTRIBUTOR = 'Data Contributor'
        DATA_ANALYST = 'Data Analyst'
        PROJECT_MANAGER = 'Project Manager'
        PLATFORM_MANAGER = 'Platform Manager'
        SYSTEM_ADMIN = 'System Administrator'
        
    def construct_GeneratedField_from_access_level(min_access_level, action):
        return AnnotationProperty(
            verbose_name = _(f'Can {action}'),
            annotation = Case(When(access_level__gte=min_access_level, then=True), default=False, output_field=models.BooleanField()),
        )
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
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
        default=1,
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
    can_view_cases = construct_GeneratedField_from_access_level(min_access_level=1, action='view cases')
    can_view_projects = construct_GeneratedField_from_access_level(min_access_level=1, action='view projects')
    can_view_cohorts = construct_GeneratedField_from_access_level(min_access_level=1, action='view cohorts')
    can_view_users = construct_GeneratedField_from_access_level(min_access_level=1, action='view users')
    can_view_datasets = construct_GeneratedField_from_access_level(min_access_level=1, action='view datasets')
    can_import_data = construct_GeneratedField_from_access_level(min_access_level=2, action='import data')
    can_manage_cases = construct_GeneratedField_from_access_level(min_access_level=2, action='manage cases')
    can_manage_cohorts = construct_GeneratedField_from_access_level(min_access_level=2, action='manage cohorts')
    can_manage_datasets = construct_GeneratedField_from_access_level(min_access_level=2, action='manage datasets')
    can_analyze_data = construct_GeneratedField_from_access_level(min_access_level=3, action='analyze data')
    can_export_data = construct_GeneratedField_from_access_level(min_access_level=3, action='export data')
    can_manage_projects = construct_GeneratedField_from_access_level(min_access_level=4, action='manage projects')
    can_access_sensitive_data = construct_GeneratedField_from_access_level(min_access_level=4, action='access sensitive data')
    can_audit_logs = construct_GeneratedField_from_access_level(min_access_level=5, action='audit logs')
    can_manage_users = construct_GeneratedField_from_access_level(min_access_level=5, action='manage users')
    is_system_admin = construct_GeneratedField_from_access_level(min_access_level=6, action='manage users')
    
    def __str__(self):
        return self.username
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(access_level__gte=0) & Q(access_level__lte=6),
                name="access_level_must_be_between_1_and_6",
            )
        ]