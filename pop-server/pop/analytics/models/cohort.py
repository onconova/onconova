from django.db import models
from django.db.models import Avg, Count, StdDev
from django.utils.translation import gettext_lazy as _

from pop.oncology.models import PatientCase
from pop.core.models import BaseModel


class CohortManager(models.Manager):
    def get_queryset(self):
        """
        Annotate the queryset with a database-level age computation.

        Age is computed using PostgreSQL's built-in AGE and EXTRACT functions.
        The computation is done on the database side, so it is both fast and
        queriable. The age is computed as the difference in years between the
        date_of_birth and either the date of death or the current date if the
        patient is alive.
        """
        return super().get_queryset().annotate(
            # Add patient age computed at database-level (fast and queriable)
            db_population=Count('cases'),
        )

class Cohort(BaseModel):

    objects = CohortManager()

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
        default = False,
    )
    frozen_set = models.ManyToManyField(
        verbose_name = _("Frozen cases"),
        help_text = _("Frozen cases"),
        to = PatientCase,
        related_name="+",
    )
    
    @property
    def description(self):
        return f"{self.name} ({self.cases.count()} cases)"
    
    @property
    def population(self):
        return self.__class__.objects.filter(pk=self.pk).values('db_population')[0]['db_population']

    @property
    def age_average(self):
        return self.__class__.get_age_average(self.cases.all())
    
    @property
    def age_stddev(self):
        return self.__class__.get_age_stddev(self.cases.all())
    
    @property
    def data_completion_average(self):
        return self.__class__.get_data_completion_average(self.cases.all())
    
    @property
    def data_completion_stddev(self):
        return self.__class__.get_data_completion_stddev(self.cases.all())

    @staticmethod
    def get_age_average(cohort):
        if not cohort.exists():
            return None
        return round(cohort.aggregate(Avg('age')).get('age__avg'),1)
    
    @staticmethod
    def get_age_stddev(cohort):
        if not cohort.count()>2:
            return None
        return round(cohort.aggregate(StdDev('age',sample=True)).get('age__stddev'),1)

    @staticmethod
    def get_data_completion_average(cohort):
        if not cohort.exists():
            return None
        return round(cohort.aggregate(Avg('data_completion_rate')).get('data_completion_rate__avg'),1)
    
    @staticmethod
    def get_data_completion_stddev(cohort):
        if not cohort.count()>2:
            return None
        return round(cohort.aggregate(StdDev('data_completion_rate',sample=True)).get('data_completion_rate__stddev'),1)


    def update_cohort_cases(self) -> models.QuerySet:        
        from pop.analytics.builder import build_query
        from pop.analytics.schemas import CohortFilterRuleset 

        if self.frozen_set.exists():
            return self.frozen_set.all()

        if self.is_public:
            cohort = PatientCase.objects.all()
        else:
            cohort = PatientCase.objects.filter(created_by=self.created_by)

        if self.include_criteria:
            query = build_query(CohortFilterRuleset.model_validate(self.include_criteria))
            cohort = cohort.filter(next(query)).distinct()

        if self.exclude_criteria:
            query = build_query(CohortFilterRuleset.model_validate(self.exclude_criteria))
            cohort = cohort.exclude(next(query)).distinct()

        cohort = cohort.union(self.manual_choices.all())
        self.cases.set(cohort)
    