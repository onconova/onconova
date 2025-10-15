import django.contrib.postgres.fields as postgres
import pghistory
from django.db import models
from django.db.models import ExpressionWrapper, F, Func
from django.db.models.functions import Cast, Coalesce, Now
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import AnnotationProperty

import onconova.core.measures as measures
import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.measures.fields import MeasurementField
from onconova.core.models import BaseModel
from onconova.oncology.models import NeoplasticEntity, PatientCase
from onconova.oncology.models.therapy_line import TherapyLine

class RadiotherapyIntentChoices(models.TextChoices):
    CURATIVE = "curative"
    PALLIATIVE = "palliative"


@pghistory.track()
class Radiotherapy(BaseModel):
    """
    Model representing a radiotherapy treatment administered to a patient.

    Attributes:
        objects (QueryablePropertiesManager): Custom manager for queryable properties.
        case (models.ForeignKey[PatientCase]): Reference to the patient case receiving radiotherapy.
        period (postgres.DateRangeField): Clinically-relevant period of radiotherapy administration.
        duration (AnnotationProperty): Duration of treatment, calculated from the period.
        targeted_entities (models.ManyToManyField[NeoplasticEntity]): Neoplastic entities targeted by the radiotherapy.
        sessions (models.PositiveIntegerField): Total number of radiotherapy sessions.
        intent (models.CharField): Treatment intent (curative or palliative).
        termination_reason (termfields.CodedConceptField[terminologies.TerminationReason]): Reason for termination of radiotherapy.
        therapy_line (models.ForeignKey[TherapyLine]): Therapy line assignment for the radiotherapy.
        description (str): Human-readable summary of the radiotherapy, including therapy line, settings, and dosages.
    """

    objects = QueryablePropertiesManager()

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_("Indicates the case of the patient who received the radiotherapy"),
        to=PatientCase,
        related_name="radiotherapies",
        on_delete=models.CASCADE,
    )
    period = postgres.DateRangeField(
        verbose_name=_("Treatment period"),
        help_text=_(
            "Clinically-relevant period during which the radiotherapy was administered to the patient."
        ),
    )
    duration = AnnotationProperty(
        verbose_name=_("Duration of treatment"),
        annotation=ExpressionWrapper(
            Func(
                Coalesce(
                    Func(
                        F("period"), function="upper", output_field=models.DateField()
                    ),
                    Cast(Now(), output_field=models.DateField()),
                    output_field=models.DateField(),
                )
                - Func(F("period"), function="lower", output_field=models.DateField()),
                function="EXTRACT",
                template="EXTRACT(EPOCH FROM %(expressions)s)",
                output_field=models.IntegerField(),
            ),
            output_field=measures.MeasurementField(
                measurement=measures.Time,
                default_unit="day",
            ),
        ),
    )
    targeted_entities = models.ManyToManyField(
        verbose_name=_("Targeted neoplastic entities"),
        help_text=_(
            "References to the neoplastic entities that were targeted by the radiotherapy"
        ),
        to=NeoplasticEntity,
        related_name="radiotherapies",
    )
    sessions = models.PositiveIntegerField(
        verbose_name=_("Total sessions"),
        help_text=_(
            "The total number of radiotherapy sessions over the treatment period."
        ),
    )
    intent = models.CharField(
        verbose_name=_("Intent"),
        help_text=_("Treatment intent of the system therapy"),
        choices=RadiotherapyIntentChoices,
        max_length=30,
    )
    termination_reason = termfields.CodedConceptField(
        verbose_name=_("Termination reason"),
        help_text=_(
            "Explanation for the premature or planned termination of the radiotherapy"
        ),
        terminology=terminologies.TreatmentTerminationReason,
        null=True,
        blank=True,
    )
    therapy_line = models.ForeignKey(
        verbose_name=_("Therapy line"),
        help_text=_("Therapy line to which the radiotherapy is assigned to"),
        to=TherapyLine,
        related_name="radiotherapies",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    @property
    def description(self):
        dosages = f"{' and '.join([dosage.description for dosage in self.dosages.all()])}"  # type: ignore
        settings = (
            f"{' and '.join([dosage.description for dosage in self.settings.all()])}"  # type: ignore
            or "Radiotherapy"
        )
        return f"{self.therapy_line.label if self.therapy_line else self.intent.capitalize()} - {settings} {dosages}"

    def assign_therapy_line(self):
        """
        Assigns therapy lines to the current case using the TherapyLine model.

        This method calls the `assign_therapy_lines` class method of `TherapyLine` 
        with the associated case, refreshes the instance from the database, 
        and returns the updated instance.

        Returns:
            (Self): The updated instance after therapy lines have been assigned and refreshed.
        """
        TherapyLine.assign_therapy_lines(self.case)
        self.refresh_from_db()
        return self


@pghistory.track()
class RadiotherapyDosage(BaseModel):
    """
    Represents a dosage record for a radiotherapy treatment.

    Attributes:
        radiotherapy (models.ForeignKey[PatientCase]): Reference to the associated Radiotherapy instance.
        fractions (models.PositiveIntegerField): Total number of radiotherapy fractions delivered.
        dose (MeasurementField[measures.RadiationDose]): Total radiation dose delivered over the full radiotherapy course.
        irradiated_volume (termfields.CodedConceptField[terminologies.RadiotherapyTreatmentLocation]): Anatomical location of the irradiated volume.
        irradiated_volume_morphology (termfields.CodedConceptField[terminologies.RadiotherapyVolumeType]): Morphology of the irradiated volume's anatomical location.
        irradiated_volume_qualifier (termfields.CodedConceptField[terminologies.RadiotherapyTreatmentLocationQualifier]): Qualifier for the anatomical location of the irradiated volume.
        description (str): Human-readable summary of the dosage, including dose, fractions, and irradiated volume.
    """

    radiotherapy = models.ForeignKey(
        verbose_name=_("Radiotherapy"),
        help_text=_("Indicates the radoptherapy where this dosage was delivered"),
        to=Radiotherapy,
        related_name="dosages",
        on_delete=models.CASCADE,
    )
    fractions = models.PositiveIntegerField(
        verbose_name=_("Total fractions"),
        help_text=_(
            "The total number of radiotherapy fractions delivered over the treatment period."
        ),
        null=True,
        blank=True,
    )
    dose = MeasurementField(
        verbose_name=_("Total radiation dose"),
        help_text=_("Total radiation dose delivered over the full radiotherapy course"),
        measurement=measures.RadiationDose,
        null=True,
        blank=True,
    )
    irradiated_volume = termfields.CodedConceptField(
        verbose_name=_("Irradiated volume"),
        help_text=_("Anatomical location of the irradiated volume"),
        terminology=terminologies.RadiotherapyTreatmentLocation,
    )
    irradiated_volume_morphology = termfields.CodedConceptField(
        verbose_name=_("Irradiated volume morphology"),
        help_text=_("Morphology of the anatomical location of the irradiated volume"),
        terminology=terminologies.RadiotherapyVolumeType,
        null=True,
        blank=True,
    )
    irradiated_volume_qualifier = termfields.CodedConceptField(
        verbose_name=_("Irradiated volume qualifier"),
        help_text=_(
            "General qualifier for the anatomical location of the irradiated volume"
        ),
        terminology=terminologies.RadiotherapyTreatmentLocationQualifier,
        null=True,
        blank=True,
    )

    @property
    def description(self):
        fractions_text = (
            f" over {self.fractions} fractions" if self.fractions is not None else ""
        )
        return f'{self.dose or "Unknown dose"}{fractions_text} to {self.irradiated_volume.display}'


@pghistory.track()
class RadiotherapySetting(BaseModel):
    """
    Represents a specific setting for a radiotherapy procedure, including its modality and technique.

    Attributes:
        radiotherapy (models.ForeignKey[PatientCase]): Reference to the associated Radiotherapy instance where this dosage was delivered.
        modality (termfields.CodedConceptField[terminologies.RadiotherapyModality]): The modality of the radiotherapy procedure (e.g., external beam, brachytherapy).
        technique (termfields.CodedConceptField[terminologies.RadiotherapyTechnique]): The technique used in the radiotherapy procedure.
        description (str): Returns a string representation combining modality and technique.
    """

    radiotherapy = models.ForeignKey(
        verbose_name=_("Radiotherapy"),
        help_text=_("Indicates the radoptherapy where this dosage was delivered"),
        to=Radiotherapy,
        related_name="settings",
        on_delete=models.CASCADE,
    )
    modality = termfields.CodedConceptField(
        verbose_name=_("Modality"),
        help_text=_("Modality of external beam or brachytherapy radiation procedures"),
        terminology=terminologies.RadiotherapyModality,
    )
    technique = termfields.CodedConceptField(
        verbose_name=_("Technique"),
        help_text=_("Technique of external beam or brachytherapy radiation procedures"),
        terminology=terminologies.RadiotherapyTechnique,
    )

    @property
    def description(self):
        return f"{self.modality}/{self.technique}"
