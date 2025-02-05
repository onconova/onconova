
from django.db import models
import django.contrib.postgres.fields as postgres
from django.utils.translation import gettext_lazy as _

from pop.core.measures.fields import MeasurementField

from pop.core.models import BaseModel 
from pop.oncology.models import PatientCase, NeoplasticEntity
from pop.oncology.models.TherapyLine import TherapyLine
import pop.terminology.fields as termfields 
import pop.terminology.models as terminologies 
import pop.core.measures as measures

class SystemicTherapy(BaseModel):

    class TreatmentIntent(models.TextChoices):
        CURATIVE = 'curative'
        PALLIATIVE = 'palliative'

    case = models.ForeignKey(
        verbose_name = _('Patient case'),
        help_text = _("Indicates the case of the patient who received the systemic therapy"),
        to = PatientCase,
        related_name = 'systemic_therapies',
        on_delete = models.CASCADE,
    )
    period = postgres.DateRangeField(
        verbose_name = _('Treatment period'),
        help_text=_("Clinically-relevant period during which the therapy was administered to the patient."),
    ) 
    targeted_entities = models.ManyToManyField(
        verbose_name = _('Targeted neoplastic entities'),
        help_text = _("References to the neoplastic entities that were targeted by the systemic therapy"),
        to = NeoplasticEntity,
        related_name = 'systemic_therapies',
    )
    #protocol = ?
    cycles = models.PositiveIntegerField(
        verbose_name = _('Cycles'),
        help_text = _("The total number of treatment cycles during the treatment period."),        
    )
    intent = models.CharField(
        verbose_name = _('Intent'),
        help_text = _("Treatment intent of the system therapy"),
        choices = TreatmentIntent,
        max_length=30,
    )
    role = termfields.CodedConceptField(
        verbose_name = _('Treatment Role'),
        help_text = _("Indicates the role of this therapy in the overall treatment strategy."),
        terminology = terminologies.TreatmentCategory,
        null=True, blank=True,
    )
    termination_reason = termfields.CodedConceptField(
        verbose_name = _('Termination reason'),
        help_text = _("Explanation for the premature or planned termination of the systemic therapy"),
        terminology = terminologies.TreatmentTerminationReason,
        null=True,blank=True,
    )
    therapy_line = models.ForeignKey(
        verbose_name = _('Therapy line'),
        help_text = _("Therapy line to which the systemic therapy is assigned to"),
        to = TherapyLine,
        related_name = 'systemic_therapies',
        on_delete = models.SET_NULL,
        null = True, blank = True,
    )

    @property
    def drugs(self):
        return [medication.drug for medication in self.medications.all()]

    @property
    def description(self):
        return f'{self.therapy_line.label if self.therapy_line else self.intent.capitalize()} - {"/".join([drug.display for drug in self.drugs])}'

    def assign_therapy_line(self):
        TherapyLine.assign_therapy_lines(self.case)
        self.refresh_from_db()
        return self

class SystemicTherapyMedication(BaseModel):

    systemic_therapy = models.ForeignKey(
        verbose_name = _('Systemic therapy'),
        help_text = _("The systemic therapy to which this medication belongs to"),
        to = SystemicTherapy,
        related_name = 'medications',
        on_delete = models.CASCADE,
    )
    drug = termfields.CodedConceptField(
        verbose_name=_('Antineoplastic Drug'),
        help_text=_("Antineoplastic drug/medication administered to the patient"),
        terminology = terminologies.AntineoplasticAgent,
    )
    route = termfields.CodedConceptField(
        verbose_name = _('Route'),
        help_text = _('Drug administration route'),
        terminology = terminologies.DosageRoute,
        blank = True, null=True,
    )
    used_offlabel = models.BooleanField(
        verbose_name=_('Off-label use'),
        help_text=_("Indicates whether a medication was used off-label at the time of administration"),
        null=True, blank=True,
    )
    within_soc = models.BooleanField(
        verbose_name = _('Within SOC'),
        help_text = _("Indicates whether a medication was within standard of care (SOC) at the time of administration."),
        null=True, blank=True,
    )    
    dosage_mass_concentration = MeasurementField(
        verbose_name= _('Dosage - Mass concentration'),
        help_text = _('Dosage of the medication expressed in mass concentration (if revelant/appliccable)'),
        measurement = measures.MassConcentration,
        null=True, blank=True,
    )
    dosage_mass = MeasurementField(
        verbose_name= _('Dosage - Fixed Mass'),
        help_text = _('Dosage of the medication expressed in a fixed mass (if revelant/appliccable)'),
        measurement = measures.Mass,
        null=True, blank=True,
    )
    dosage_volume = MeasurementField(
        verbose_name= _('Dosage - Volume'),
        help_text = _('Dosage of the medication expressed in a volume (if revelant/appliccable)'),
        measurement = measures.Volume,
        null=True, blank=True,
    )
    dosage_mass_surface = MeasurementField(
        verbose_name= _('Dosage - Mass per body surface'),
        help_text = _('Dosage of the medication expressed in a mass per body surface area (if revelant/appliccable)'),
        measurement = measures.MassPerArea,
        null=True, blank=True,
    )
    dosage_rate_mass_concentration = MeasurementField(
        verbose_name= _('Dosage rate - Mass concentration'),
        help_text = _('Dosage rate of the medication expressed in mass concentration (if revelant/appliccable)'),
        measurement = measures.MassConcentrationPerTime,
        null=True, blank=True,
    )
    dosage_rate_mass = MeasurementField(
        verbose_name= _('Dosage rate - Fixed Mass'),
        help_text = _('Dosage rate of the medication expressed in a fixed mass (if revelant/appliccable)'),
        measurement = measures.MassPerTime,
        null=True, blank=True,
    )
    dosage_rate_volume = MeasurementField(
        verbose_name= _('Dosage rate - Volume'),
        help_text = _('Dosage rate of the medication expressed in a volume (if revelant/appliccable)'),
        measurement = measures.VolumePerTime,
        null=True, blank=True,
    )
    dosage_rate_mass_surface = MeasurementField(
        verbose_name= _('Dosage rate - Mass per body surface'),
        help_text = _('Dosage rate of the medication expressed in a mass per body surface area (if revelant/appliccable)'),
        measurement = measures.MassPerAreaPerTime,
        null=True, blank=True,
    )
  
    @property
    def description(self):
        return f'{self.drug}'
