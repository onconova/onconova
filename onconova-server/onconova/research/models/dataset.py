import pghistory
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import Count, Max, Q, Value
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from queryable_properties.properties import AnnotationProperty

from onconova.core.models import BaseModel
from onconova.research.models.project import Project


@pghistory.track()
class Dataset(BaseModel):

    name = models.CharField(
        verbose_name=_("Dataset name"),
        help_text=_("Name of the dataset"),
        max_length=255,
    )
    summary = models.TextField(
        verbose_name=_("Dataset summary"),
        help_text=_("Summary of the dataset"),
        null=True,
        blank=True,
    )
    rules = models.JSONField(
        verbose_name=_("Rules"),
        help_text=_("Dataset composition rules"),
        default=list,
    )
    project = models.ForeignKey(
        verbose_name=_("Project"),
        help_text=_("Project that the dataset is part of"),
        to=Project,
        on_delete=models.CASCADE,
        related_name="datasets",
    )
    last_export = AnnotationProperty(
        verbose_name=_("Last export"),
        annotation=Max("events__pgh_created_at", filter=Q(events__pgh_label="export")),
    )
    total_exports = AnnotationProperty(
        verbose_name=_("Last export"),
        annotation=Count("events__pgh_id", filter=Q(events__pgh_label="export")),
    )
    cohorts_ids = AnnotationProperty(
        verbose_name=_("Cohorts Ids"),
        annotation=Coalesce(
            ArrayAgg(
                "events__pgh_context__cohort",
                filter=Q(events__pgh_label="export"),
                distinct=True,
            ),
            Value([]),
        ),
    )

    def save(self, *args, **kwargs):
        from onconova.research.schemas.dataset import DatasetRule

        # Validate the rules
        if not isinstance(self.rules, list):
            raise ValueError("Rules must be a valid list")
        for rule in self.rules:
            DatasetRule.model_validate(rule)
        super().save(*args, **kwargs)

    @property
    def description(self):
        return f'Dataset "{self.name}"'
        return f'Dataset "{self.name}"'
