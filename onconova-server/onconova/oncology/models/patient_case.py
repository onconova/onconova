import random
import string

import pghistory
from django.apps import apps
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import (
    Case,
    Count,
    Exists,
    ExpressionWrapper,
    F,
    Func,
    Min,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.expressions import RawSQL
from django.db.models.functions import Cast, Coalesce, ExtractYear, Round
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import (
    AnnotationGetterMixin,
    AnnotationMixin,
    AnnotationProperty,
    QueryableProperty,
    RelatedExistenceCheckProperty,
)

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel


class PatientCaseDataCategories(models.TextChoices):
    COMORBIDITIES_ASSESSMENTS = "comorbidities-assessments"
    FAMILY_HISTORIES = "family-histories"
    GENOMIC_SIGNATURES = "genomic-signatures"
    GENOMIC_VARIANTS = "genomic-variants"
    LIFESTYLES = "lifestyles"
    COMORBIDITIES = "comorbidities"
    NEOPLASTIC_ENTITIES = "neoplastic-entities"
    PERFORMANCE_STATUS = "performance-status"
    RADIOTHERAPIES = "radiotherapies"
    RISK_ASSESSMENTS = "risk-assessments"
    STAGINS = "stagings"
    SURGERIES = "surgeries"
    SYSTEMIC_THERAPIES = "systemic-therapies"
    TUMOR_MARKERS = "tumor-markers"
    VITALS = "vitals"
    TUMOR_BOARD_REVIEWS = "tumor-board-reviews"
    ADVERSE_EVENTS = "adverse-events"
    THERAPY_RESPONSES = "therapy-responses"


class VitalStatus(models.TextChoices):
    ALIVE = "alive"
    DECEASED = "deceased"
    UNKNOWN = "unknown"

DATA_CATEGORIES_COUNT = len(list(PatientCaseDataCategories))


def events_common_table_expression():
    event_tables = [
        model.pgh_event_model._meta.db_table # type: ignore
        for model in apps.get_app_config("oncology").get_models()
        if hasattr(model, "pgh_event_model")
        and hasattr(model.pgh_event_model, "case_id") # type: ignore
    ]
    union_selects = [
        f"SELECT ({table}.pgh_context->>'username')::varchar as username, {table}.pgh_created_at, {table}.pgh_label FROM {table} WHERE {table}.case_id = {PatientCase._meta.db_table}.id  AND {table}.pgh_context ? 'username'"
        for table in event_tables
    ]
    case_event_table = PatientCase.pgh_event_model._meta.db_table # type: ignore
    union_selects.append(
        f"SELECT ({case_event_table}.pgh_context->>'username')::varchar as username, {case_event_table}.pgh_created_at, {case_event_table}.pgh_label FROM {case_event_table} WHERE {case_event_table}.id = {PatientCase._meta.db_table}.id  AND {case_event_table}.pgh_context ? 'username'"
    )
    return " UNION ALL ".join(union_selects)


class UpdatedAtProperty(AnnotationGetterMixin, QueryableProperty):

    def get_annotation(self, cls):
        return RawSQL(
            f"""
            (
                SELECT cte.pgh_created_at
                FROM (
                    {events_common_table_expression()}
                ) AS cte WHERE cte.pgh_label = 'update'
                ORDER BY cte.pgh_created_at DESC LIMIT 1
            )
        """,
            [],
            output_field=models.DateField(),
        )


class ContributorsProperty(AnnotationGetterMixin, QueryableProperty):

    def get_annotation(self, cls):
        return Coalesce(
            RawSQL(
                f"""
            (
                SELECT ARRAY_AGG(DISTINCT cte.username)
                FROM (
                    {events_common_table_expression()}
                ) AS cte
            )
        """,
                [],
                output_field=ArrayField(models.CharField()),
            ),
            Value([]),
        )


@pghistory.track()
class PatientCase(BaseModel):

    objects = QueryablePropertiesManager()

    class ConsentStatus(models.TextChoices):
        VALID = "valid"
        REVOKED = "revoked"
        UNKNOWN = "unknown"

    pseudoidentifier = models.CharField(
        verbose_name=_("Pseudoidentifier"),
        help_text=_("Pseudoidentifier of the patient"),
        max_length=40,
        unique=True,
        editable=False,
    )
    clinical_center = models.CharField(
        verbose_name=_("Medical center"),
        help_text=_("Medical center where the patient data originally resides"),
        max_length=200,
    )
    clinical_identifier = models.CharField(
        verbose_name=_("Clinical identifier"),
        help_text=_(
            "Unique clinical identifier (typically the clinical information system identifier) unique for a physical patient"
        ),
        max_length=100,
    )
    consent_status = models.CharField(
        verbose_name=_("Consent status"),
        help_text=_(
            "Status of the general consent by the patient for the use of their data for research purposes"
        ),
        max_length=20,
        choices=ConsentStatus,
        default=ConsentStatus.UNKNOWN,
    )
    gender = termfields.CodedConceptField(
        verbose_name=_("Gender"),
        help_text=_("Gender of the patient for legal/administrative purposes"),
        terminology=terminologies.AdministrativeGender,
    )
    race = termfields.CodedConceptField(
        verbose_name=_("Race"),
        help_text=_("Race of the patient"),
        terminology=terminologies.Race,
        null=True,
        blank=True,
    )
    sex_at_birth = termfields.CodedConceptField(
        verbose_name=_("Birth sex"),
        help_text=_("Sex assigned at birth"),
        terminology=terminologies.BirthSex,
        blank=True,
        null=True,
    )
    gender_identity = termfields.CodedConceptField(
        verbose_name=_("Gender identity"),
        help_text=_(
            "The patient's innate sense of their gender as reported"
        ),
        terminology=terminologies.GenderIdentity,
        null=True,
        blank=True,
    )
    date_of_birth = models.DateField(
        verbose_name=_("Date of birth"),
        help_text=_(
            "Anonymized date of birth (year/month). The day is set to the first day of the month by convention."
        ),
    )
    age = AnnotationProperty(
        verbose_name=_("Age"),
        annotation=ExpressionWrapper(
            ExtractYear(
                Func(
                    Case(
                        When(date_of_death__isnull=False, then=F("date_of_death")),
                        When(end_of_records__isnull=False, then=F("end_of_records")),
                        default=Func(function="NOW"),
                    ),
                    F("date_of_birth"),
                    function="AGE",
                ),
            ),
            output_field=models.IntegerField(),
        ),
    )
    has_neoplastic_entities = RelatedExistenceCheckProperty("neoplastic_entities")
    age_at_diagnosis = AnnotationProperty(
        verbose_name=_("Age at diagnosis"),
        annotation=Case(
            When(Q(has_neoplastic_entities=False), then=None),
            default=ExtractYear(
                Func(
                    Min("neoplastic_entities__assertion_date"),
                    F("date_of_birth"),
                    function="AGE",
                ),
            ),
            output_field=models.IntegerField(),
        ),
    )
    vital_status =  models.CharField(
        verbose_name=_("Vital status"),
        help_text=_(
            "Whether the patient is known to be alive or decaeased or is unknkown."
        ),
        max_length=20,
        choices=VitalStatus,
        default=VitalStatus.UNKNOWN,
    )
    date_of_death = models.DateField(
        verbose_name=_("Date of death"),
        help_text=_(
            "Anonymized date of death (year/month). The day is set to the first day of the month by convention."
        ),
        null=True,
        blank=True,
    )
    cause_of_death = termfields.CodedConceptField(
        verbose_name=_("Cause of death"),
        help_text=_("Classification of the cause of death."),
        terminology=terminologies.CauseOfDeath,
        null=True,
        blank=True,
    )
    data_completion_rate = AnnotationProperty(
        verbose_name=_("Data completion rate"),
        annotation=Round(
            Cast(Count("completed_data_categories"), output_field=models.FloatField())
            / DATA_CATEGORIES_COUNT
            * 100
        ),
    )
    total_entities = AnnotationProperty(annotation=Count("neoplastic_entities"))
    overall_survival = AnnotationProperty(
        verbose_name=_("Overall survival since diagnosis in months"),
        annotation=Case(
            When(total_entities=0, then=None),
            default=Func(
                Cast(
                    Case(
                        When(date_of_death__isnull=False, then=F("date_of_death")),
                        When(end_of_records__isnull=False, then=F("end_of_records")),
                        default=Func(function="NOW"),
                    ),
                    models.DateField(),
                )
                - Min(F("neoplastic_entities__assertion_date")),
                function="EXTRACT",
                template="EXTRACT(EPOCH FROM %(expressions)s)",
                output_field=models.IntegerField(),
            )
            / Value(3600 * 24 * 30.436875),
            output_field=models.FloatField(),
        ),
    )
    end_of_records = models.DateField(
        verbose_name=_("End of records"),
        help_text=_(
            "Date of the last known record about the patient if lost to followup or vital status is unknown."
        ),
        null=True,
        blank=True,
    )
    updated_at = UpdatedAtProperty(
        verbose_name=_("Updated at"),
    )
    contributors = ContributorsProperty(
        verbose_name=_("Contributors"),
    )

    @property
    def description(self):
        return f"ONCONOVA Case {self.pseudoidentifier}"

    def _generate_random_id(self):
        """
        Generates a random identifier string for a patient record.

        The format of the string is 'X.NNN.YYY.ZZ', where 'X' is a random uppercase letter,
        'NNN' is a random 3-digit number, 'YYY' is a random 3-digit number, and 'ZZ' is a random 2-digit number.

        This function is used to generate a unique identifier for a patient record if one is not
        specified when a patient record is created.
        """
        digit = lambda N: "".join([str(random.randint(1, 9)) for _ in range(N)])
        return f"{random.choice(string.ascii_letters).upper()}.{digit(4)}.{digit(3)}.{digit(2)}"

    def save(self, *args, **kwargs):
        # If an ID has not been manually specified, add an automated one
        """
        If an ID has not been manually specified, add an automated one.

        When saving a patient record, if no ID is specified, this method will generate
        a random one and check it against existing records in the database. If a conflict
        is found, it will generate a new ID and check it again. This ensures that the ID
        is unique.

        Also, ensures that the date of birth and date of death are properly de-identified before
        storing them in the database.
        """
        if not self.pseudoidentifier:
            # Generate random digits
            new_pseudoidentifier = self._generate_random_id()
            # Check for ID clashes in the database
            while PatientCase.objects.filter(
                pseudoidentifier=new_pseudoidentifier
            ).exists():
                new_pseudoidentifier = self._generate_random_id()
            # Set the ID for the patient
            self.pseudoidentifier = new_pseudoidentifier
        # Ensure the date_of_birth is anonymized
        if self.date_of_birth.day != 1:
            self.date_of_birth = self.date_of_birth.replace(day=1)
        if self.date_of_death and self.date_of_death.day != 1:
            self.date_of_death = self.date_of_death.replace(day=1)
        if self.end_of_records and self.end_of_records.day != 1:
            self.end_of_records = self.end_of_records.replace(day=1)
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["clinical_center", "clinical_identifier"],
                name="unique_clinical_identifier_per_center",
            ),
            models.CheckConstraint(
                check=Q(date_of_birth__day=1),
                name="date_of_birth_must_be_first_of_month",
                violation_error_message="Birthdate must be the first day of the month",
            ),
            models.CheckConstraint(
                check=Q(date_of_death__day=1),
                name="date_of_death_must_be_first_of_month",
                violation_error_message="Birthdate must be the first day of the month",
            ),
            models.CheckConstraint(
                check=Q(end_of_records__day=1),
                name="end_of_records_must_be_first_of_month",
                violation_error_message="End of records must be the first day of the month",
            ),
            models.CheckConstraint(
                check=Case(
                    When(Q(Q(vital_status=VitalStatus.ALIVE) & Q(date_of_death__isnull=False)), then=Value(False)),
                    When(Q(Q(vital_status=VitalStatus.UNKNOWN) & Q(date_of_death__isnull=False)), then=Value(False)),
                    When(Q(Q(vital_status=VitalStatus.DECEASED) & Q(date_of_death__isnull=True)), then=Value(False)),
                    default=True
                ), # type: ignore
                name="vital_status_date_of_death_combinations",
                violation_error_message="Invalid vital status and date of death combination",
            ),
            models.CheckConstraint(
                check=Case(
                    When(Q(Q(vital_status=VitalStatus.UNKNOWN) & Q(end_of_records__isnull=True)), then=Value(False)),
                    default=True
                ), # type: ignore
                name="unknown_vital_status_requires_end_of_records",
                violation_error_message="Unknown vital status requires a valid end of records date.",
            ),
            models.CheckConstraint(
                check=Case(
                    When(Q(Q(vital_status=VitalStatus.ALIVE) & Q(cause_of_death__isnull=False)), then=Value(False)),
                    When(Q(Q(vital_status=VitalStatus.UNKNOWN) & Q(cause_of_death__isnull=False)), then=Value(False)),
                    default=True
                ), # type: ignore
                name="cause_of_death_only_for_deceased",
                violation_error_message="Cause of death can only be assigned to deceased cases.",
            ),
        ]


@pghistory.track()
class PatientCaseDataCompletion(BaseModel):

    PatientCaseDataCategories = PatientCaseDataCategories
    DATA_CATEGORIES_COUNT = DATA_CATEGORIES_COUNT

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_("Patient case who's data category has been marked as completed."),
        to=PatientCase,
        on_delete=models.CASCADE,
        related_name="completed_data_categories",
    )
    category = models.CharField(
        verbose_name=_("Finalized data category"),
        help_text=_(
            "Indicates the categories of a patient case, whose data entries are deemed to be complete and/or up-to-date with the primary records."
        ),
        max_length=500,
        choices=PatientCaseDataCategories,
        blank=True,
    )

    @property
    def description(self):
        return f'Category "{self.category}" for case {self.case.pseudoidentifier} marked as completed by {self.created_by} on {self.created_at}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["case", "category"],
                name="unique_data_categories",
                violation_error_message="Data categories cannot be repeated for a patient case",
            )
        ]
        ]
