from collections import Counter, OrderedDict
from typing import Tuple

import pghistory
from django.db import models
from django.db.models import Avg, Count, F, StdDev
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import AnnotationProperty

from onconova.core.aggregates import Median, Percentile25, Percentile75
from onconova.core.models import BaseModel
from onconova.oncology.models import PatientCase
from onconova.research.models.dataset import *
from onconova.research.models.project import Project


@pghistory.track()
class Cohort(BaseModel):

    objects = QueryablePropertiesManager()

    name = models.CharField(
        verbose_name=_("Cohort name"),
        help_text=_("Name of the cohort"),
        max_length=255,
    )
    cases = models.ManyToManyField(
        verbose_name=_("Cases"),
        help_text=_("Cases composing the cohort"),
        to=PatientCase,
        related_name="cohorts",
    )
    include_criteria = models.JSONField(
        verbose_name=_("Inclusion criteria"),
        help_text="JSON object defining inclusion criteria",
        null=True,
        blank=True,
    )
    exclude_criteria = models.JSONField(
        verbose_name=_("Exclusion criteria"),
        help_text="JSON object defining exclusion criteria",
        null=True,
        blank=True,
    )
    manual_choices = models.ManyToManyField(
        verbose_name=_("Manually added cases"),
        help_text=_("Manually added cases"),
        to=PatientCase,
        related_name="+",
    )
    frozen_set = models.ManyToManyField(
        verbose_name=_("Frozen cases"),
        help_text=_("Frozen cases"),
        to=PatientCase,
        related_name="+",
    )
    population = AnnotationProperty(
        verbose_name=_("Population"),
        annotation=Count("cases"),
    )
    project = models.ForeignKey(
        verbose_name=_("Project"),
        help_text=_("Project to which the cohort is associated"),
        to=Project,
        on_delete=models.PROTECT,
        related_name="cohorts",
        null=True,
        blank=True,
    )

    @property
    def description(self) -> str:
        return f"{self.name} ({self.cases.count()} cases)"

    @property
    def valid_cases(self):
        return self.cases.filter(consent_status=PatientCase.ConsentStatus.VALID)

    @staticmethod
    def get_cohort_trait_average(
        cases, trait: str, **filters
    ) -> Tuple[float, float] | None:
        if filters:
            cases = cases.filter(**filters)
        if not cases.exists():
            return None
        queryset = cases.aggregate(Avg(trait), StdDev(trait))
        return queryset[f"{trait}__avg"], queryset[f"{trait}__stddev"]

    @staticmethod
    def get_cohort_trait_median(
        cases, trait: str, **filters
    ) -> Tuple[float, Tuple[float, float]] | None:
        if filters:
            cases = cases.filter(**filters)
        if not cases.exists():
            return None
        queryset = cases.aggregate(
            Median(trait), Percentile25(trait), Percentile75(trait)
        )
        median = queryset[f"{trait}__median"]
        iqr = (queryset[f"{trait}__p25"], queryset[f"{trait}__p75"])
        return median, iqr

    @staticmethod
    def get_cohort_trait_counts(
        cases, trait: str, anonymization=None, **filters
    ) -> dict:
        if filters:
            cases = cases.filter(**filters)
        if not cases:
            return OrderedDict()
        values = cases.annotate(trait=F(trait)).values_list("trait", flat=True)
        if anonymization:
            values = [anonymization(value) if value else value for value in values]
        return OrderedDict(
            [
                (str(key), (count, round(count / len(values) * 100.0, 4)))
                for key, count in Counter(values).items()
            ]
        )

    def update_cohort_cases(self):
        from onconova.research.schemas.cohort import CohortRuleset

        if self.frozen_set.exists():
            return self.frozen_set.all()

        if not self.include_criteria and not self.exclude_criteria:
            return []

        cohort = PatientCase.objects.all()

        if self.include_criteria:
            query = CohortRuleset.model_validate(
                self.include_criteria
            ).convert_to_query()
            cohort = cohort.filter(next(query)).distinct()

        if self.exclude_criteria:
            query = CohortRuleset.model_validate(
                self.exclude_criteria
            ).convert_to_query()
            cohort = cohort.exclude(next(query)).distinct()

        cohort = cohort.union(self.manual_choices.all())
        self.cases.set(cohort)
