import uuid 
import pghistory
import pghistory.models
from django.db import models
from django.db.models import Q, Subquery, OuterRef, Min, Max, Value
from django.db.models.functions import Cast, Replace, Coalesce
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.expressions import ArraySubquery

from queryable_properties.properties import AnnotationProperty, SubqueryObjectProperty
from queryable_properties.managers import QueryablePropertiesManager

from .user import User 

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

        events_model = getattr(self, 'pgh_event_model', None)
        if events_model:
            events_related_name = events_model._meta.get_field('pgh_obj')._related_name
            AnnotationProperty(
                annotation=Min(f'{events_related_name}__pgh_created_at', filter=Q(events__pgh_label='create')),
            ).contribute_to_class(self.__class__, 'created_at')
            
            AnnotationProperty(
                annotation=Max(f'{events_related_name}__pgh_created_at', filter=Q(events__pgh_label='update')),
            ).contribute_to_class(self.__class__, 'updated_at')
            
            AnnotationProperty(
                annotation=Replace(
                    Cast(Subquery(pghistory.models.Events.objects
                            .annotate(pgh_obj_pk=Cast('pgh_obj_id', models.UUIDField()))
                            .filter(pgh_obj_pk=OuterRef('pk'), pgh_label='create')
                            .exclude(pgh_context__username__isnull=True)
                            .values('pgh_context__username')[:1]
                    ), models.CharField()),
                    Value('"'),Value('')
                )
            ).contribute_to_class(self.__class__, 'created_by')

            query = Q(pgh_id__in=OuterRef(f'{events_related_name}__pgh_id'))
            if hasattr(self, 'parent_events'):
                query = query | Q(pgh_id__in=OuterRef(f'parent_events__pgh_id'))

            AnnotationProperty(
                annotation=ArrayAgg(
                    Replace(Cast(
                        pghistory.models.Events.objects
                                .filter(query, pgh_label='update')
                                .exclude(pgh_context__username__isnull=True)
                                .values('pgh_context__username')[:1]
                    ,models.CharField()),Value('"'),Value('')
                    )
                )
            ).contribute_to_class(self.__class__, 'updated_by')
            
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
