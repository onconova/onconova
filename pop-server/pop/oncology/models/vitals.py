import pghistory

from django.db import models
from django.utils.translation import gettext_lazy as _

from pop.core.models import BaseModel
from pop.core.measures.fields import MeasurementField
from pop.oncology.models import PatientCase
import pop.core.measures as measures

from queryable_properties.properties import AnnotationProperty
from queryable_properties.managers import QueryablePropertiesManager


@pghistory.track()
class Vitals(BaseModel):

    objects = QueryablePropertiesManager()

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_("Indicates the case of the patient who's vitals are assesed"),
        to=PatientCase,
        related_name="vitals",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Assessment date"),
        help_text=_("Clinically-relevant date at which the vitals were recorded."),
    )
    height = MeasurementField(
        verbose_name=_("Height"),
        help_text=_("Height of the patient"),
        measurement=measures.Distance,
        default_unit="m",
        null=True,
        blank=True,
    )
    weight = MeasurementField(
        verbose_name=_("Weight"),
        help_text=_("Weight of the patient"),
        measurement=measures.Mass,
        default_unit="kg",
        null=True,
        blank=True,
    )
    body_mass_index = AnnotationProperty(
        verbose_name=_("Bodymass"),
        annotation=models.ExpressionWrapper(
            models.F("weight") / (models.F("height") * models.F("height")),
            output_field=MeasurementField(
                measurement=measures.MassPerArea,
                default_unit="kg__square_meter",
            ),
        ),
    )
    blood_pressure_systolic = MeasurementField(
        verbose_name=_("Systolic blood pressure"),
        help_text=_("Systolic blood pressure of the patient"),
        measurement=measures.Pressure,
        default_unit="mmHg",
        null=True,
        blank=True,
    )
    blood_pressure_diastolic = MeasurementField(
        verbose_name=_("Diastolic blood pressure"),
        help_text=_("Diastolic blood pressure of the patient"),
        measurement=measures.Pressure,
        default_unit="mmHg",
        null=True,
        blank=True,
    )
    temperature = MeasurementField(
        verbose_name=_("Temperature"),
        help_text=_("Temperature of the patient"),
        measurement=measures.Temperature,
        default_unit="celsius",
        null=True,
        blank=True,
    )

    @property
    def description(self):
        return ", ".join(
            [
                str(vital)
                for vital in [
                    self.height,
                    self.weight,
                    self.body_mass_index,
                    self.temperature,
                    self.blood_pressure_diastolic,
                    self.blood_pressure_systolic,
                    self.temperature,
                ]
                if vital
            ]
        )
