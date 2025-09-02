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
    """
    Represents a dataset within a research project.

    Attributes:
        name (models.CharField): The name of the dataset.
        summary (models.TextField): A brief summary of the dataset (optional).
        rules (models.JSONField): Composition rules for the dataset, validated as a list.
        project (models.ForeignKey[Project]): Reference to the associated Project.
        last_export (AnnotationProperty): Timestamp of the last export event.
        total_exports (AnnotationProperty): Total number of export events.
        cohorts_ids (AnnotationProperty): List of cohort IDs associated with export events.
    """

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
        """
        Saves the current instance after validating its rules.

        This method performs the following steps:
        1. Imports the DatasetRule schema for rule validation.
        2. Ensures that the 'rules' attribute is a list; raises ValueError if not.
        3. Validates each rule in the 'rules' list using DatasetRule.model_validate.
        4. Calls the superclass's save method to persist the instance.

        Args:
            args (list): Variable length argument list passed to the superclass save method.
            kwargs (dict): Arbitrary keyword arguments passed to the superclass save method.

        Raises:
            ValueError: If 'rules' is not a list.
            ValidationError: If any rule fails validation via DatasetRule.model_validate.
        """
        from onconova.research.schemas.dataset import DatasetRule

        # Validate the rules
        if not isinstance(self.rules, list):
            raise ValueError("Rules must be a valid list")
        for rule in self.rules:
            DatasetRule.model_validate(rule)
        super().save(*args, **kwargs)

    @property
    def description(self):
        """
        Returns a string describing the dataset.

        Returns:
            (str): A formatted description of the dataset.
        """
        return f'Dataset "{self.name}"'
