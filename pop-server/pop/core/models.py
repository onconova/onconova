import uuid 

from django.db import models
from django.db.models import Case, When, Q
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from queryable_properties.properties import MappingProperty
from queryable_properties.properties import AnnotationProperty

class User(AbstractUser):
        
    class AccessRoles(models.TextChoices):
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
    access_level = models.IntegerField(
        verbose_name = _('Access level'),
        help_text = _('Level of access of the user in terms of permissions'),
        validators = [MinValueValidator(1), MaxValueValidator(7)],        
        default=1,
    )
    role = MappingProperty(
        verbose_name = _('Role'),
        attribute_path = 'access_level',
        output_field = models.CharField(choices=AccessRoles),
        mappings= (
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
    can_import_data = construct_GeneratedField_from_access_level(min_access_level=2, action='import data')
    can_manage_cases = construct_GeneratedField_from_access_level(min_access_level=2, action='manage cases')
    can_manage_cohorts = construct_GeneratedField_from_access_level(min_access_level=2, action='manage cohorts')
    can_analyze_data = construct_GeneratedField_from_access_level(min_access_level=3, action='analyze data')
    can_export_data = construct_GeneratedField_from_access_level(min_access_level=3, action='export data')
    can_manage_projects = construct_GeneratedField_from_access_level(min_access_level=4, action='manage projects')
    can_access_sensitive_data = construct_GeneratedField_from_access_level(min_access_level=4, action='access sensitive data')
    can_audit_logs = construct_GeneratedField_from_access_level(min_access_level=5, action='audit logs')
    can_manage_users = construct_GeneratedField_from_access_level(min_access_level=5, action='manage users')
    is_system_admin = construct_GeneratedField_from_access_level(min_access_level=6, action='manage users')
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(access_level__gte=1) & Q(access_level__lte=6),
                name="access_level_must_be_between_1_and_6",
            )
        ]

class BaseModel(models.Model):
    """
    A base model class that provides common fields and methods for all models.

    This class provides common fields and methods that are used by all models in
    the application. The fields provided by this class include a unique identifier,
    creation and modification times, and the users who created and modified the
    data. The methods provided by this class include a description property that
    returns a human-readable description of the model instance, and a method to
    generate a unique identifier for a model instance.

    Attributes:
        auto_id: A unique identifier for the model instance.
        id: A human-readable identifier for the model instance.
        created_at: The date and time at which the model instance was created.
        updated_at: The date and time at which the model instance was last modified.
        created_by: The user who created the model instance.
        updated_by: The users who modified the model instance.
    """

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    created_by = models.ForeignKey(
        help_text=_('The user who created the original data'),
        to=User,
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
    )
    updated_by = models.ManyToManyField(
        help_text=_('The user(s) who updated the data since its creation'),
        to=User,
        related_name='+'
    )
    external_source = models.CharField(
        verbose_name = _('External data source'),
        help_text=_('The digital source of the data, relevant for automated data'),
        null=True, blank=True
    )
    external_source_id = models.CharField(
        verbose_name = _('External data source Id'),
        help_text=_('The data identifier at the digital source of the data, relevant for automated data'),
        null=True, blank=True
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """
        Initializes the model instance.

        This method is the constructor for the model instance. It is called when a
        new instance is created. It calls the parent class's constructor and then
        checks if the instance has a primary key and identifier. If the instance
        does not have an identifier, it generates a unique identifier for the
        instance using the `_generate_unique_id` method.

        :param args: The positional arguments to be passed to the parent class
                     constructor.
        :param kwargs: The keyword arguments to be passed to the parent class
                       constructor.
        """
        super().__init__(*args, **kwargs)
        if not self.pk and not self.id:
            self.id = self._generate_unique_id()

    @property
    def description(self):
        """
        A human-readable description of the model instance.

        This property should be implemented by subclasses to provide a human-readable
        description of the model instance. The description should be a string that is
        suitable for display to users.

        Returns:
            str: A human-readable description of the model instance.
        """
        raise NotImplementedError("Subclasses must implement the description property")

    def __str__(self):
        return self.description
