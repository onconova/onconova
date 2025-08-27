import pghistory

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from pop.core.models import BaseModel
from pop.oncology.models import PatientCase
from pop.oncology.models.radiotherapy import Radiotherapy
from pop.oncology.models.systemic_therapy import (
    SystemicTherapy,
    SystemicTherapyMedication,
)
from pop.oncology.models.surgery import Surgery
import pop.terminology.fields as termfields
import pop.terminology.models as terminologies


@pghistory.track()
class AdverseEvent(BaseModel):

    class AdverseEventOutcome(models.TextChoices):
        RESOLVED = "resolved"
        RESOLVED_WITH_SEQUELAE = "resolved-with-sequelae"
        RECOVERING = "recovering"
        ONGOIND = "ongoing"
        FATAL = "fatal"
        UNKNOWN = "unknown"

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_(
            "Indicates the case of the patient who had the adverse event being recorded"
        ),
        to=PatientCase,
        related_name="adverse_events",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Event date"),
        help_text=_("Clinically-relevant date at which the adverse event ocurred."),
    )
    event = termfields.CodedConceptField(
        verbose_name=_("Adverse event"),
        help_text=_("Classification of the adverse event using CTCAE criteria"),
        terminology=terminologies.AdverseEventTerm,
    )
    grade = models.PositiveSmallIntegerField(
        verbose_name=_("Grade"),
        help_text=_(
            "The grade associated with the severity of an adverse event, using CTCAE criteria."
        ),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    outcome = models.CharField(
        verbose_name=_("Date resolved"),
        help_text=_("The date when the adverse event ended or returned to baseline."),
        choices=AdverseEventOutcome,
        max_length=50,
    )
    date_resolved = models.DateField(
        verbose_name=_("Date resolved"),
        help_text=_("The date when the adverse event ended or returned to baseline."),
        blank=True,
        null=True,
    )
    is_resolved = models.GeneratedField( # type: ignore
        verbose_name=_("Is resolved"),
        help_text=_("Indicates whether the adverse event has been resolved"),
        expression=models.Case(
            models.When(
                models.Q(outcome=AdverseEventOutcome.RESOLVED)
                | models.Q(outcome=AdverseEventOutcome.RESOLVED_WITH_SEQUELAE),
                then=models.Value(True),
            ),
            default=models.Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
    )

    @property
    def description(self):
        causes = " and ".join(
            [cause.description for cause in self.suspected_causes.all()] # type: ignore
        )
        return " ".join([self.event.display or "", f"(grade {self.grade})", causes])


@pghistory.track()
class AdverseEventSuspectedCause(BaseModel):

    class AdverseEventCausality(models.TextChoices):
        UNRELATED = "unrelated"
        UNLEKELY_RELATED = "unlikely-related"
        POSSIBLY_RELATED = "possibly-related"
        PROBABLY_RELATED = "probably-related"
        DEFINITELY_RELATED = "definitely-related"
        CONDITIONALLY_RELATED = "conditionally-related"

    adverse_event = models.ForeignKey(
        verbose_name=_("Adverse event"),
        help_text=_("Adverse event to which this suspected cause belongs to"),
        to=AdverseEvent,
        related_name="suspected_causes",
        on_delete=models.CASCADE,
    )
    systemic_therapy = models.ForeignKey(
        verbose_name=_("Suspected systemic therapy"),
        help_text=_("Systemic therapy suspected to be the cause of the adverse event"),
        to=SystemicTherapy,
        related_name="adverse_events",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    medication = models.ForeignKey(
        verbose_name=_("Suspected systemic therapy medication"),
        help_text=_(
            "Systemic therapy medication suspected to be the cause of the adverse event"
        ),
        to=SystemicTherapyMedication,
        related_name="adverse_events",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    radiotherapy = models.ForeignKey(
        verbose_name=_("Suspected radiotherapy"),
        help_text=_("Radiotherapy suspected to be the cause of the adverse event"),
        to=Radiotherapy,
        related_name="adverse_events",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    surgery = models.ForeignKey(
        verbose_name=_("Suspected surgery"),
        help_text=_("Surgery suspected to be the cause of the adverse event"),
        to=Surgery,
        related_name="adverse_events",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    causality = models.CharField(
        verbose_name=_("Causality"),
        help_text=_("Assessment of the potential causality"),
        choices=AdverseEventCausality,
        max_length=50,
        blank=True,
        null=True,
    )

    @property
    def cause(self):
        return (
            self.systemic_therapy
            or self.medication
            or self.radiotherapy
            or self.surgery
        )

    @property
    def description(self):
        if self.causality:
            return f'{self.causality.replace("-"," ").capitalize()} to {self.cause}'
        else:
            return f'due to {self.cause}'
            


@pghistory.track()
class AdverseEventMitigation(BaseModel):

    class AdverseEventMitigationCategory(models.TextChoices):
        ADJUSTMENT = "adjustment"
        PHARMACOLOGICAL = "pharmacological"
        PROCEDIRE = "procedure"

    adverse_event = models.ForeignKey(
        verbose_name=_("Adverse event"),
        help_text=_("Adverse event to which this mitigation belongs to"),
        to=AdverseEvent,
        related_name="mitigations",
        on_delete=models.CASCADE,
    )
    category = models.CharField(
        verbose_name=_("Mitigation category"),
        help_text=_("Type of mitigation employed"),
        choices=AdverseEventMitigationCategory,
        max_length=50,
    )
    adjustment = termfields.CodedConceptField(
        verbose_name=_("Treatment Adjustment"),
        help_text=_(
            "Classification of the adjustment of systemic anti-cancer treatment used to mitigate the adverse event (if applicable)"
        ),
        terminology=terminologies.AdverseEventMitigationTreatmentAdjustment,
        null=True,
        blank=True,
    )
    drug = termfields.CodedConceptField(
        verbose_name=_("Pharmacological drug"),
        help_text=_(
            "Classification of the pharmacological treatment used to mitigate the adverse event (if applicable)"
        ),
        terminology=terminologies.AdverseEventMitigationDrug,
        null=True,
        blank=True,
    )
    procedure = termfields.CodedConceptField(
        verbose_name=_("Procedure"),
        help_text=_(
            "Classification of the non-pharmacological procedure used to mitigate the adverse event (if applicable)"
        ),
        terminology=terminologies.AdverseEventMitigationProcedure,
        null=True,
        blank=True,
    )
    management = termfields.CodedConceptField(
        verbose_name=_("Management"),
        help_text=_("Management type of the adverse event mitigation"),
        terminology=terminologies.AdverseEventMitigationManagement,
        null=True,
        blank=True,
    )

    @property
    def description(self):
        if self.adjustment and self.adjustment.display:
            return f"Mitigated by therapy {self.adjustment.display.lower()}"
        if self.drug and self.drug.display:
            return f"Mitigated by {self.drug.display.lower()}"
        if self.procedure and self.procedure.display:
            return f"Mitigated by {self.procedure.display.lower()}"
        return "Mitigation"
