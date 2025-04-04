from typing import Tuple
from collections import OrderedDict, Counter

from django.db import models
from django.db.models import Avg, Count, StdDev, F
from django.utils.translation import gettext_lazy as _

from queryable_properties.properties import AnnotationProperty
from queryable_properties.managers import QueryablePropertiesManager

from pop.analytics.aggregates import Median, Percentile25, Percentile75
from pop.oncology.models import PatientCase
from pop.core.models import BaseModel


class Cohort(BaseModel):

    objects = QueryablePropertiesManager()

    name = models.CharField(
        verbose_name = _("Cohort name"),
        help_text = _("Name of the cohort"),
        max_length=255, 
    )
    cases = models.ManyToManyField(
        verbose_name = _("Cases"),
        help_text = _("Cases composing the cohort"),
        to = PatientCase,
        related_name="cohorts",
    )
    include_criteria = models.JSONField(
        verbose_name = _("Inclusion criteria"),
        help_text="JSON object defining inclusion criteria",
        null = True, blank = True,
    )
    exclude_criteria = models.JSONField(
        verbose_name = _("Exclusion criteria"),
        help_text="JSON object defining exclusion criteria",
        null = True, blank = True,
    )
    manual_choices = models.ManyToManyField(
        verbose_name = _("Manually added cases"),
        help_text = _("Manually added cases"),
        to = PatientCase,
        related_name="+",
    )
    is_public = models.BooleanField(
        verbose_name = _("Is public?"),
        help_text = _("Whether the cohort is public"),
        default = True,
    )
    frozen_set = models.ManyToManyField(
        verbose_name = _("Frozen cases"),
        help_text = _("Frozen cases"),
        to = PatientCase,
        related_name="+",
    )
    population = AnnotationProperty(
        verbose_name = _("Population"),
        annotation = Count('cases'),
    )
    
    @property
    def description(self) -> str:
        return f"{self.name} ({self.cases.count()} cases)"
    
    def get_cohort_trait_average(self, trait: str) -> Tuple[float, float]:
        if not self.cases.exists():
            return None
        queryset = self.cases.aggregate(Avg(trait), StdDev(trait))
        return queryset[f'{trait}__avg'], queryset[f'{trait}__stddev']

    def get_cohort_trait_median(self, trait: str) -> Tuple[float, Tuple[float, float]]:
        if not self.cases.exists():
            return None
        queryset = self.cases.aggregate(Median(trait), Percentile25(trait), Percentile75(trait))
        median = queryset[f'{trait}__median']
        iqr = (queryset[f'{trait}__p25'], queryset[f'{trait}__p75'])
        return median, iqr

    def get_cohort_trait_counts(self, trait: str) -> dict:
        if not self.cases.exists():
            return None
        values = self.cases.annotate(trait=F(trait)).values_list('trait', flat=True)
        return OrderedDict([(str(key), (count, round(count/values.count()*100.0,4))) for key, count in Counter(values).items()])

    def update_cohort_cases(self) -> models.QuerySet:        
        from pop.analytics.schemas import CohortRuleset 

        if self.frozen_set.exists():
            return self.frozen_set.all()

        if not self.include_criteria and not self.exclude_criteria:
            return []

        if self.include_criteria:
            query = CohortRuleset.model_validate(self.include_criteria).convert_to_query()
            cohort = cohort.filter(next(query)).distinct()

        if self.exclude_criteria:
            query = CohortRuleset.model_validate(self.exclude_criteria).convert_to_query()
            cohort = cohort.exclude(next(query)).distinct()

        cohort = cohort.union(self.manual_choices.all())
        self.cases.set(cohort)
    