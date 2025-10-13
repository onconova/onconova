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
from onconova.oncology.models.patient_case import PatientCase, PatientCaseConsentStatusChoices
from onconova.research.models.dataset import *
from onconova.research.models.project import Project


@pghistory.track()
class Cohort(BaseModel):
    """
    Represents a cohort of patient cases within a research project.

    Attributes:
        objects (QueryablePropertiesManager): Custom manager for queryable properties.
        name (models.CharField): Name of the cohort.
        cases (models.ManyToManyField[PatientCase]): Patient cases composing the cohort.
        include_criteria (models.JSONField): JSON object defining inclusion criteria for cohort membership.
        exclude_criteria (models.JSONField): JSON object defining exclusion criteria for cohort membership.
        manual_choices (models.ManyToManyField[PatientCase]): Manually added patient cases.
        frozen_set (models.ManyToManyField[PatientCase]): Cases that are frozen and not updated by criteria.
        population (AnnotationProperty): Annotated count of cases in the cohort.
        project (models.ForeignKey[Project]): Project to which the cohort is associated.
    """

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
        """
        Returns a string describing the cohort, including its name and the number of cases.

        Returns:
            (str): A formatted string with the cohort name and case count.
        """
        return f"{self.name} ({self.cases.count()} cases)"

    @property
    def valid_cases(self):
        """
        Returns a queryset of cases with a consent status marked as VALID.

        Filters the related cases to include only those where the consent_status
        is set to PatientCase.ConsentStatus.VALID.

        Returns:
            (QuerySet[PatientCase]): A queryset of valid PatientCase instances.
        """
        return self.cases.filter(consent_status=PatientCaseConsentStatusChoices.VALID)

    @staticmethod
    def get_cohort_trait_average(
        cases, trait: str, **filters
    ) -> Tuple[float, float] | None:
        """
        Calculates the average and standard deviation of a specified trait for a given queryset of cases,
        optionally applying additional filters.

        Args:
            cases (QuerySet[PatientCase]): A Django queryset representing the cohort of cases.
            trait (str): The name of the trait/field to aggregate.
            filters (dict): Optional keyword arguments to filter the queryset.

        Returns:
            Tuple[float, float] | None: A tuple containing the average and standard deviation of the trait,
            or None if the filtered queryset is empty.
        """
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
        """
        Calculates the median and interquartile range (IQR) for a specified trait within a cohort.

        Args:
            cases (QuerySet[PatientCase]): A Django QuerySet representing the cohort of cases.
            trait (str): The name of the trait/field to compute statistics for.
            filters (dict): Optional keyword arguments to filter the cases QuerySet.

        Returns:
            Optional[Tuple[float, Tuple[float, float]]]: 
                A tuple containing the median value and a tuple of the 25th and 75th percentiles (IQR) for the trait.
                Returns None if no cases match the filters.
        """
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
        """
        Calculates the counts and percentage distribution of a specified trait within a cohort of cases.

        Args:
            cases (QuerySet[PatientCase]): A Django QuerySet or iterable of case objects.
            trait (str): The name of the trait/field to count within the cases.
            anonymization (callable, optional): A function to anonymize trait values. Defaults to None.
            filters (dict): Additional keyword arguments to filter the cases QuerySet.

        Returns:
            (dict): An OrderedDict mapping trait values (as strings) to a tuple of (count, percentage),
                  where percentage is rounded to 4 decimal places.
        """
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
        """
        Updates the cohort's cases based on inclusion and exclusion criteria.

        - If a frozen set of cases exists, returns those cases.
        - If neither inclusion nor exclusion criteria are provided, returns an empty list.
        - Otherwise, filters PatientCase objects according to the inclusion criteria,
          then excludes cases matching the exclusion criteria.
        - Manually selected cases are added to the cohort.
        - The resulting set of cases is assigned to the cohort.

        Returns:
            (QuerySet | list): The updated set of cohort cases.
        """
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
