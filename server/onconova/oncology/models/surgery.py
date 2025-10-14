import pghistory
from django.db import models
from django.utils.translation import gettext_lazy as _

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import NeoplasticEntity, PatientCase
from onconova.oncology.models.therapy_line import TherapyLine

class SurgeryIntentChoices(models.TextChoices):
    """
    An enumeration of possible treatment intents for a surgical procedure.

    Attributes:
        CURATIVE: Indicates that the surgery is performed with the intention to cure the patient.
        PALLIATIVE: Indicates that the surgery is performed to relieve symptoms or improve quality of life, without aiming for a cure.
    """
    CURATIVE = "curative"
    PALLIATIVE = "palliative"
    
@pghistory.track()
class Surgery(BaseModel):
    """
    Represents a surgical procedure performed on a patient within an oncology context.

    Attributes:
        case (models.ForeignKey[PatientCase]): Reference to the patient case associated with the surgery.
        date (models.DateField): The clinically relevant date when the surgical procedure was performed.
        targeted_entities (models.ManyToManyField[NeoplasticEntities]): Neoplastic entities targeted by the surgery.
        procedure (termfields.CodedConceptField[terminologies.SurgicalProcedure]): The specific surgical procedure performed, coded using a controlled terminology.
        intent (models.CharField[TreatmentIntent]): Therapeutic intent of the surgery (curative or palliative).
        bodysite (termfields.CodedConceptField[terminologies.CancerTopography]): Anatomical location where the surgery was performed.
        bodysite_qualifier (termfields.CodedConceptField[terminologies.CancerTopography]): Qualifier for the anatomical location of the surgery.
        bodysite_laterality (termfields.CodedConceptField[terminologies.CancerLaterality]): Laterality of the anatomical location of the surgery.
        outcome (termfields.CodedConceptField[terminologies.SurgicalOutcome]): Outcome of the surgical procedure.
        therapy_line (models.ForeignKey[TherapyLine]): Therapy line to which the surgery is assigned.
        description (str): Returns a human-readable description of the surgery, including therapy line or intent and procedure.
    """

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_(
            "Indicates the case of the patient who received the surgical procedure"
        ),
        to=PatientCase,
        related_name="surgeries",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Assessment date"),
        help_text=_("Clinically-relevant date of the surgical procedure."),
    )
    targeted_entities = models.ManyToManyField(
        verbose_name=_("Targeted neoplastic entities"),
        help_text=_(
            "References to the neoplastic entities that were targeted by the surgery"
        ),
        to=NeoplasticEntity,
        related_name="surgeries",
    )
    procedure = termfields.CodedConceptField(
        verbose_name=_("Surgical procedure"),
        help_text=_("The specific surgical procedure that was performed"),
        terminology=terminologies.SurgicalProcedure,
    )
    intent = models.CharField(
        verbose_name=_("Intent"),
        help_text=_("Therapeutic intent of the surgery"),
        choices=SurgeryIntentChoices,
        max_length=30,
    )
    bodysite = termfields.CodedConceptField(
        verbose_name=_("Anatomical location"),
        help_text=_("Anatomical location of the surgery"),
        terminology=terminologies.CancerTopography,
        null=True,
        blank=True,
    )
    bodysite_qualifier = termfields.CodedConceptField(
        verbose_name=_("Anatomical location qualifier"),
        help_text=_("General qualifier for the anatomical location of the surgery"),
        terminology=terminologies.BodyLocationQualifier,
        null=True,
        blank=True,
    )
    bodysite_laterality = termfields.CodedConceptField(
        verbose_name="Anatomical location laterality",
        help_text=_("Laterality for the anatomical location of the surgery"),
        terminology=terminologies.LateralityQualifier,
        null=True,
        blank=True,
    )
    outcome = termfields.CodedConceptField(
        verbose_name=_("Outcome"),
        help_text=_("The outcome of the surgery"),
        terminology=terminologies.ProcedureOutcome,
        blank=True,
        null=True,
    )
    therapy_line = models.ForeignKey(
        verbose_name=_("Therapy line"),
        help_text=_("Therapy line to which the surgery is assigned to"),
        to=TherapyLine,
        related_name="surgeries",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    @property
    def description(self):
        return f"{self.therapy_line.label if self.therapy_line else self.intent.capitalize()} - {self.procedure}"

    def assign_therapy_line(self):
        TherapyLine.assign_therapy_lines(self.case)
        self.refresh_from_db()
        return self
