import uuid 
import pghistory
import pghistory.models
from django.db import models
from django.db.models import Q, Min, Max
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.fields.json import KeyTextTransform
from django.utils.functional import lazy


from queryable_properties.properties import AnnotationProperty
from queryable_properties.managers import QueryablePropertiesManager

from .user import User 

class UntrackedBaseModel(models.Model):
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
    """
    
    objects = QueryablePropertiesManager()

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
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


class BaseModel(UntrackedBaseModel):
    
    created_at = AnnotationProperty(
        annotation=Min(f'events__pgh_created_at', filter=Q(events__pgh_label='create')),
    )
    updated_at = AnnotationProperty(
        annotation=Max(f'events__pgh_created_at', filter=Q(events__pgh_label='update')),
    )
    created_by = AnnotationProperty(
        annotation=Min(KeyTextTransform('username', 'events__pgh_context', filter=Q(events__pgh_label='create')))
    )
    updated_by = AnnotationProperty(
        annotation=ArrayAgg(KeyTextTransform('username', 'events__pgh_context', filter=Q(events__pgh_label='create')), distinct=True)
    )

    class Meta:
        abstract = True