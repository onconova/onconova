import pghistory 

from django.db import models
from django.utils.translation import gettext_lazy as _
from pop.core.models import BaseModel

@pghistory.track()
class Dataset(BaseModel):

    name = models.CharField(
        verbose_name = _("Dataset name"),
        help_text = _("Name of the dataset"),
        max_length=255, 
    )
    rules = models.JSONField(
        verbose_name = _("Rules"),
        help_text = _("Dataset composition rules"),
        default=list,
    )
    is_public = models.BooleanField(
        verbose_name = _("Is public?"),
        help_text = _("Whether the cohort is public"),
        default = True,
    )
    
    def save(self,*args, **kwargs):
        from pop.analytics.schemas.datasets import DatasetRule
        # Validate the rules
        if not isinstance(self.rules, list):
            raise ValueError('Rules must be a valid list')
        for rule in self.rules:
            DatasetRule.model_validate(rule)
        super().save(*args, **kwargs)
    
    @property
    def description(self):
        return f'Dataset "{self.name}"'

