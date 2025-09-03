import uuid
from pghistory.models import Event
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import Max, Min, Q
from django.db.models.fields.json import KeyTextTransform
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import AnnotationProperty

# Import models from submodules to be discoverable by Django
from .auth.models import *


class UntrackedBaseModel(models.Model):
    """
    Abstract base model providing common fields and behaviors for models that are not tracked by Django's built-in mechanisms.
    This model uses a custom manager (`QueryablePropertiesManager`) and includes fields for external data source tracking.

    Attributes:
        objects (QueryablePropertiesManager): The default manager for querying model instances with annotated properties.
        id (models.UUIDField): Primary key, automatically generated UUID.
        external_source (models.CharField): Optional. The digital source of the data, useful for automated data imports.
        external_source_id (models.CharField): Optional. The identifier of the data at the external source.
    """

    objects = QueryablePropertiesManager()

    id = models.UUIDField(primary_key=True, help_text=_("Unique identifier of the resource (UUID v4)."), default=uuid.uuid4, editable=False)
    external_source = models.CharField(
        verbose_name=_("External data source"),
        help_text=_("The digital source of the data, relevant for automated data"),
        null=True,
        blank=True,
    )
    external_source_id = models.CharField(
        verbose_name=_("External data source Id"),
        help_text=_(
            "The data identifier at the digital source of the data, relevant for automated data"
        ),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    @property
    def description(self):
        """A human-readable description of the model instance.

        Subclasses must implement this property to provide a string suitable for display to users.

        Raises:
            NotImplementedError: If the subclass does not implement the description property.
        """
        raise NotImplementedError("Subclasses must implement the description property")

    def __str__(self):
        try:
            return self.description
        except NotImplementedError:
            return f"{self.__class__.__name__} instance (description not implemented)"


class BaseModel(UntrackedBaseModel):
    """
    Abstract base model that provides annotated properties for tracking creation and update metadata.

    Attributes:
        created_at (AnnotationProperty): The earliest creation timestamp from related events with label `create`.
        updated_at (AnnotationProperty): The latest update timestamp from related events with label `update`.
        created_by (AnnotationProperty): The username associated with the creation event.
        updated_by (AnnotationProperty): A list of distinct usernames associated with update events.

    Note:
        This model is abstract and should be inherited by other models to include audit fields.
    """
    
    events: models.QuerySet[Event]
    
    created_at = AnnotationProperty(
        annotation=Min("events__pgh_created_at", filter=Q(events__pgh_label="create")),
    )
    updated_at = AnnotationProperty(
        annotation=Max("events__pgh_created_at", filter=Q(events__pgh_label="update")),
    )
    created_by = AnnotationProperty(
        annotation=Min(
            KeyTextTransform("username", "events__pgh_context"),
            filter=Q(events__pgh_label="create"),
        )
    )
    updated_by = AnnotationProperty(
        annotation=ArrayAgg(
            KeyTextTransform("username", "events__pgh_context"),
            filter=Q(events__pgh_label="update"),
            distinct=True,
        )
    )

    class Meta:
        abstract = True
