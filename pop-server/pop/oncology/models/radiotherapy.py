import pghistory

from django.db import models
from django.db.models import ExpressionWrapper, Value, Func, F
import django.contrib.postgres.fields as postgres
from django.utils.translation import gettext_lazy as _

from queryable_properties.properties import AnnotationProperty
from queryable_properties.managers import QueryablePropertiesManager

from pop.core.measures.fields import MeasurementField
from pop.core.models import BaseModel
from pop.oncology.models import PatientCase, NeoplasticEntity
from pop.oncology.models.therapy_line import TherapyLine
import pop.terminology.fields as termfields
import pop.terminology.models as terminologies
import pop.core.measures as measures


@pghistory.track()
class Radiotherapy(BaseModel):

    objects = QueryablePropertiesManager()

    class TreatmentIntent(models.TextChoices):
        CURATIVE = "curative"
        PALLIATIVE = "palliative"

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
                Func(F("period"), function="upper", output_field=models.DateField())
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
        choices=TreatmentIntent,
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
        dosages = (
            f"{' and '.join([dosage.description for dosage in self.dosages.all()])}"
        )
        settings = (
            f"{' and '.join([dosage.description for dosage in self.settings.all()])}"
            or "Radiotherapy"
        )
        return f"{self.therapy_line.label if self.therapy_line else self.intent.capitalize()} - {settings} {dosages}"

    def assign_therapy_line(self):
        TherapyLine.assign_therapy_lines(self.case)
        self.refresh_from_db()
        return self


@pghistory.track()
class RadiotherapyDosage(BaseModel):

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
