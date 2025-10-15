import django.contrib.postgres.fields as postgres
import pghistory
from django.contrib.postgres.aggregates import StringAgg
from django.db import models
from django.db.models import Case, ExpressionWrapper, F, Func, Max, Q, Value, When
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

class SystemicTherapyIntentChoices(models.TextChoices):
    CURATIVE = "curative"
    PALLIATIVE = "palliative"

@pghistory.track()
class SystemicTherapy(BaseModel):
    """
    Represents a systemic therapy administered to a patient within an oncology context.

    Attributes:
        objects (QueryablePropertiesManager): Custom manager for querying properties.
        case (models.ForeignKey[PatientCase]): Reference to the patient case receiving the therapy.
        period (postgres.DateRangeField): Clinically relevant period during which the therapy was administered.
        duration (AnnotationProperty): Duration of treatment, calculated from the period.
        targeted_entities (models.ManyToManyField[NeoplasticEntity]): Neoplastic entities targeted by the therapy.
        cycles (models.PositiveIntegerField): Total number of treatment cycles during the period.
        intent (models.CharField): Treatment intent (curative or palliative).
        adjunctive_role (termfields.CodedConceptField[terminologies.AdjunctiveRole]): Role of adjunctive therapy, if applicable.
        is_adjunctive (models.GeneratedField): Indicates if the therapy is adjunctive.
        termination_reason (termfields.CodedConceptField[terminologies.TerminationReason]): Reason for termination of the therapy.
        therapy_line (models.ForeignKey[TherapyLine]): Therapy line assignment for the systemic therapy.
        drug_combination (AnnotationProperty): String representation of the drug combination used.
        drugs (list): List of drugs used in the therapy.
        description (str): Human-readable description of the therapy, including line and drugs.

    """

    objects = QueryablePropertiesManager()


    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_(
            "Indicates the case of the patient who received the systemic therapy"
        ),
        to=PatientCase,
        related_name="systemic_therapies",
        on_delete=models.CASCADE,
    )
    period = postgres.DateRangeField(
        verbose_name=_("Treatment period"),
        help_text=_(
            "Clinically-relevant period during which the therapy was administered to the patient."
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
            "References to the neoplastic entities that were targeted by the systemic therapy"
        ),
        to=NeoplasticEntity,
        related_name="systemic_therapies",
    )
    # protocol = ?
    cycles = models.PositiveIntegerField(
        verbose_name=_("Cycles"),
        help_text=_(
            "The total number of treatment cycles during the treatment period."
        ),
        null=True,
        blank=True,
    )
    intent = models.CharField(
        verbose_name=_("Intent"),
        help_text=_("Treatment intent of the system therapy"),
        choices=SystemicTherapyIntentChoices,
        max_length=30,
    )
    adjunctive_role = termfields.CodedConceptField(
        verbose_name=_("Treatment Role"),
        help_text=_("Indicates the role of the adjunctive therapy (if applicable)."),
        terminology=terminologies.AdjunctiveTherapyRole,
        null=True,
        blank=True,
    )
    is_adjunctive = models.GeneratedField(  # type: ignore
        verbose_name=_("Treatment Role"),
        help_text=_(
            "Indicates whether it is adjunctive therapy instead of a primary therapy "
        ),
        expression=Case(
            When(Q(adjunctive_role__isnull=False), then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
    )
    termination_reason = termfields.CodedConceptField(
        verbose_name=_("Termination reason"),
        help_text=_(
            "Explanation for the premature or planned termination of the systemic therapy"
        ),
        terminology=terminologies.TreatmentTerminationReason,
        null=True,
        blank=True,
    )
    therapy_line = models.ForeignKey(
        verbose_name=_("Therapy line"),
        help_text=_("Therapy line to which the systemic therapy is assigned to"),
        to=TherapyLine,
        related_name="systemic_therapies",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    drug_combination = AnnotationProperty(
        verbose_name=_("Drug combination"),
        annotation=Coalesce(
            StringAgg("medications__drug__display", "/"),
            Value(""),
            output_field=models.TextField(),
        ),
    )

    @property
    def drugs(self):
        return [medication.drug for medication in self.medications.all()]  # type: ignore

    @property
    def description(self):
        return f'{self.therapy_line.label if self.therapy_line else self.intent.capitalize()} - {"/".join([drug.display for drug in self.drugs])}'

    def assign_therapy_line(self):
        TherapyLine.assign_therapy_lines(self.case)
        self.refresh_from_db()
        return self


@pghistory.track()
class SystemicTherapyMedication(BaseModel):
    """
    Represents a medication administered as part of a systemic therapy regimen.

    Attributes:
        systemic_therapy (models.ForeignKey[SystemicTherapy]): Reference to the associated SystemicTherapy instance.
        drug (termfields.CodedConceptField[AntineoplasticAgent]): The antineoplastic drug/medication administered to the patient.
        route (termfields.CodedConceptField[DosageRoute]): The route of drug administration (optional).
        used_offlabel (models.BooleanField): Indicates if the medication was used off-label at the time of administration (optional).
        within_soc (models.BooleanField): Indicates if the medication was within standard of care (SOC) at the time of administration (optional).
        dosage_mass_concentration (MeasurementField[measures.MassConcentration]): Dosage expressed in mass concentration (optional).
        dosage_mass (MeasurementField[measures.Mass]): Dosage expressed as a fixed mass (optional).
        dosage_volume (MeasurementField[measures.Volume]): Dosage expressed in volume (optional).
        dosage_mass_surface (MeasurementField[measures.MassSurfaceArea]): Dosage expressed in mass per body surface area (optional).
        dosage_rate_mass_concentration (MeasurementField[measures.MassConcentration]): Dosage rate expressed in mass concentration per time (optional).
        dosage_rate_mass (MeasurementField[measures.Mass]): Dosage rate expressed as a fixed mass per time (optional).
        dosage_rate_volume (MeasurementField[measures.Volume]): Dosage rate expressed in volume per time (optional).
        dosage_rate_mass_surface (MeasurementField[measures.MassSurfaceArea]): Dosage rate expressed in mass per body surface area per time (optional).
        description (str): Returns a string representation of the drug.
    """

    systemic_therapy = models.ForeignKey(
        verbose_name=_("Systemic therapy"),
        help_text=_("The systemic therapy to which this medication belongs to"),
        to=SystemicTherapy,
        related_name="medications",
        on_delete=models.CASCADE,
    )
    drug = termfields.CodedConceptField(
        verbose_name=_("Antineoplastic Drug"),
        help_text=_("Antineoplastic drug/medication administered to the patient"),
        terminology=terminologies.AntineoplasticAgent,
    )
    route = termfields.CodedConceptField(
        verbose_name=_("Route"),
        help_text=_("Drug administration route"),
        terminology=terminologies.DosageRoute,
        blank=True,
        null=True,
    )
    used_offlabel = models.BooleanField(
        verbose_name=_("Off-label use"),
        help_text=_(
            "Indicates whether a medication was used off-label at the time of administration"
        ),
        null=True,
        blank=True,
    )
    within_soc = models.BooleanField(
        verbose_name=_("Within SOC"),
        help_text=_(
            "Indicates whether a medication was within standard of care (SOC) at the time of administration."
        ),
        null=True,
        blank=True,
    )
    dosage_mass_concentration = MeasurementField(
        verbose_name=_("Dosage - Mass concentration"),
        help_text=_(
            "Dosage of the medication expressed in mass concentration (if revelant/appliccable)"
        ),
        measurement=measures.MassConcentration,
        null=True,
        blank=True,
    )
    dosage_mass = MeasurementField(
        verbose_name=_("Dosage - Fixed Mass"),
        help_text=_(
            "Dosage of the medication expressed in a fixed mass (if revelant/appliccable)"
        ),
        measurement=measures.Mass,
        null=True,
        blank=True,
    )
    dosage_volume = MeasurementField(
        verbose_name=_("Dosage - Volume"),
        help_text=_(
            "Dosage of the medication expressed in a volume (if revelant/appliccable)"
        ),
        measurement=measures.Volume,
        null=True,
        blank=True,
    )
    dosage_mass_surface = MeasurementField(
        verbose_name=_("Dosage - Mass per body surface"),
        help_text=_(
            "Dosage of the medication expressed in a mass per body surface area (if revelant/appliccable)"
        ),
        measurement=measures.MassPerArea,
        null=True,
        blank=True,
    )
    dosage_rate_mass_concentration = MeasurementField(
        verbose_name=_("Dosage rate - Mass concentration"),
        help_text=_(
            "Dosage rate of the medication expressed in mass concentration (if revelant/appliccable)"
        ),
        measurement=measures.MassConcentrationPerTime,
        null=True,
        blank=True,
    )
    dosage_rate_mass = MeasurementField(
        verbose_name=_("Dosage rate - Fixed Mass"),
        help_text=_(
            "Dosage rate of the medication expressed in a fixed mass (if revelant/appliccable)"
        ),
        measurement=measures.MassPerTime,
        null=True,
        blank=True,
    )
    dosage_rate_volume = MeasurementField(
        verbose_name=_("Dosage rate - Volume"),
        help_text=_(
            "Dosage rate of the medication expressed in a volume (if revelant/appliccable)"
        ),
        measurement=measures.VolumePerTime,
        null=True,
        blank=True,
    )
    dosage_rate_mass_surface = MeasurementField(
        verbose_name=_("Dosage rate - Mass per body surface"),
        help_text=_(
            "Dosage rate of the medication expressed in a mass per body surface area (if revelant/appliccable)"
        ),
        measurement=measures.MassPerAreaPerTime,
        null=True,
        blank=True,
    )

    @property
    def description(self):
        return f"{self.drug}"
