import pghistory

from django.db import models
from django.utils.translation import gettext_lazy as _
from pop.core.models import BaseModel
from pop.research.models.project import Project


@pghistory.track()
class Dataset(BaseModel):

    name = models.CharField(
        verbose_name=_("Dataset name"),
        help_text=_("Name of the dataset"),
        max_length=255,
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

    def save(self, *args, **kwargs):
        from pop.research.schemas.dataset import DatasetRule

        # Validate the rules
        if not isinstance(self.rules, list):
            raise ValueError("Rules must be a valid list")
        for rule in self.rules:
            DatasetRule.model_validate(rule)
        super().save(*args, **kwargs)

    @property
    def description(self):
        return f'Dataset "{self.name}"'
