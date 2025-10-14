import pghistory
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import PatientCase
from onconova.oncology.models.radiotherapy import Radiotherapy
from onconova.oncology.models.surgery import Surgery
from onconova.oncology.models.systemic_therapy import (
    SystemicTherapy,
    SystemicTherapyMedication,
)



class AdverseEventOutcomeChoices(models.TextChoices):
    """
    Enumeration of possible outcomes for an adverse event.

    Attributes:
        RESOLVED: The adverse event has been resolved.
        RESOLVED_WITH_SEQUELAE: The adverse event has resolved but with lasting effects (sequelae).
        RECOVERING: The subject is currently recovering from the adverse event.
        ONGOING: The adverse event is ongoing.
        FATAL: The adverse event resulted in death.
        UNKNOWN: The outcome of the adverse event is unknown.
    """
    RESOLVED = "resolved"
    RESOLVED_WITH_SEQUELAE = "resolved-with-sequelae"
    RECOVERING = "recovering"
    ONGOING = "ongoing"
    FATAL = "fatal"
    UNKNOWN = "unknown"


class AdverseEventSuspectedCauseCausalityChoices(models.TextChoices):
    UNRELATED = "unrelated"
    UNLEKELY_RELATED = "unlikely-related"
    POSSIBLY_RELATED = "possibly-related"
    PROBABLY_RELATED = "probably-related"
    DEFINITELY_RELATED = "definitely-related"
    CONDITIONALLY_RELATED = "conditionally-related"


class AdverseEventMitigationCategoryChoices(models.TextChoices):
    ADJUSTMENT = "adjustment"
    PHARMACOLOGICAL = "pharmacological"
    PROCEDIRE = "procedure"


@pghistory.track()
class AdverseEvent(BaseModel):
    """
    Represents an adverse event experienced by a patient during oncology treatment.

    Attributes:
        case (models.ForeignKey[PatientCase]): Reference to the patient case associated with the adverse event.
        date (models.DateField): The clinically relevant date when the adverse event occurred.
        event (termfields.CodedConceptField[terminologies.AdverseEventTerm]): Classification of the adverse event using CTCAE criteria.
        grade (models.PositiveSmallIntegerField): Severity grade of the adverse event, following CTCAE criteria (0-5).
        outcome (models.CharField): Outcome of the adverse event, selected from predefined choices.
        date_resolved (models.DateField): Date when the adverse event ended or returned to baseline.
        is_resolved (models.BooleanField): Indicates whether the adverse event has been resolved.
    """
    
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
        choices=AdverseEventOutcomeChoices,
        max_length=50,
    )
    date_resolved = models.DateField(
        verbose_name=_("Date resolved"),
        help_text=_("The date when the adverse event ended or returned to baseline."),
        blank=True,
        null=True,
    )
    is_resolved = models.GeneratedField(  # type: ignore
        verbose_name=_("Is resolved"),
        help_text=_("Indicates whether the adverse event has been resolved"),
        expression=models.Case(
            models.When(
                models.Q(outcome=AdverseEventOutcomeChoices.RESOLVED)
                | models.Q(outcome=AdverseEventOutcomeChoices.RESOLVED_WITH_SEQUELAE),
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
            [cause.description[0].lower() + cause.description[1:] for cause in self.suspected_causes.all()]  # type: ignore
        )
        return " ".join([self.event.display or "", f"(grade {self.grade})", causes])


@pghistory.track()
class AdverseEventSuspectedCause(BaseModel):
    """
    Represents a suspected cause of an adverse event in oncology.

    Attributes:
        adverse_event (models.ForeignKey): Reference to the associated AdverseEvent.
        systemic_therapy (models.ForeignKey[SystemicTherapy]): Suspected systemic therapy causing the adverse event.
        medication (models.ForeignKey[SystemicTherapyMedication]): Suspected medication causing the adverse event.
        radiotherapy (models.ForeignKey[Radiotherapy]): Suspected radiotherapy causing the adverse event.
        surgery (models.ForeignKey[Surgery]): Suspected surgery causing the adverse event.
        causality (models.CharField[AdverseEventCausality]): Assessment of the potential causality, chosen from predefined options.
    """

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
        choices=AdverseEventSuspectedCauseCausalityChoices,
        max_length=50,
        blank=True,
        null=True,
    )

    @property
    def cause(self):
        """
        Determines the cause of the adverse event by checking related treatment attributes.

        Returns:
            (Any): The first non-falsy value among systemic_therapy, medication, radiotherapy, or surgery, indicating the treatment responsible for the adverse event. If none are present, returns None.
        """
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
            return f"due to {self.cause}"


@pghistory.track()
class AdverseEventMitigation(BaseModel):
    """
    Model representing a mitigation strategy for an adverse event in oncology.

    Attributes:
        adverse_event (models.ForeignKey[AdverseEvent]): Reference to the associated AdverseEvent instance.
        category (models.CharField[AdverseEventMitigationCategory]): Type of mitigation employed, chosen from adjustment, pharmacological, or procedure.
        adjustment (termfields.CodedConceptField[terminologies.AdverseEventMitigationTreatmentAdjustment]): Classification of treatment adjustment used to mitigate the adverse event (optional).
        drug (termfields.CodedConceptField[terminologies.AdverseEventMitigationDrug]): Classification of pharmacological treatment used to mitigate the adverse event (optional).
        procedure (termfields.CodedConceptField[terminologies.AdverseEventMitigationProcedure]): Classification of non-pharmacological procedure used to mitigate the adverse event (optional).
        management (termfields.CodedConceptField[terminologies.AdverseEventMitigationManagement]): Management type of the adverse event mitigation (optional).
    """

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
        choices=AdverseEventMitigationCategoryChoices,
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
