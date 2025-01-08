
from django.db import models
from django.utils.translation import gettext_lazy as _


from pop.core.models import BaseModel 
from pop.core.fields import MeasurementField
from pop.oncology.models import PatientCase 
import pop.core.measures as measures
import pop.terminology.fields as termfields 
import pop.terminology.models as terminologies 


class Lifestyle(BaseModel):

    case = models.ForeignKey(
        verbose_name = _('Patient case'),
        help_text = _("Indicates the case of the patient who's lifestyle is assesed"),
        to = PatientCase,
        related_name = 'lifestyles',
        on_delete = models.CASCADE,
    )
    date = models.DateField(
        verbose_name = _('Assessment date'),
        help_text=_("Clinically-relevant date at which the patient's lifetyle was assessed and recorded."),
    ) 
    smoking_status = termfields.CodedConceptField(
        verbose_name = _('Alcohol consumption'),
        help_text = _("Frequency of alcohol consumption"),
        terminology = terminologies.SmokingStatus,  
        null = True, blank = True
    )  
    smoking_packyears = models.FloatField(
        verbose_name = _('Smoking packyears'),
        help_text = _("Smoking pack-years (if applicable)"),
        null = True, blank = True
    )  
    smoking_quited = MeasurementField(
        verbose_name=_('Time since quitted smoking'),
        help_text=_("Estimated time since quitting smoking (if applicable)"),
        measurement = measures.Time,
        default_unit = 'year',
        null = True, blank = True,
    )
    alcohol_consumption = termfields.CodedConceptField(
        verbose_name = _('Alcohol consumption'),
        help_text = _("Frequency of alcohol consumption"),
        terminology = terminologies.AlcoholConsumptionFrequency,  
        null = True, blank = True
    )  
    night_sleep = MeasurementField(
        verbose_name = _('Night sleep'),
        help_text = _("Estimated average sleep time per night"),
        measurement = measures.Time,
        default_unit = 'hour',
        null = True, blank = True
    )  
    recreational_drugs = termfields.CodedConceptField(
        verbose_name = _('Recreational drugs'),
        help_text = _("Any recreational drug(s) used by the patient"),
        terminology = terminologies.RecreationalDrug,  
        multiple = True,
    ) 
    exposures = termfields.CodedConceptField(
        verbose_name = _('Exposures'),
        help_text = _("Environmental or occupational exposures to hazards or carcinogenic agents"),
        terminology = terminologies.ExposureAgent,  
        multiple = True,
    ) 
    
    @property
    def description(self):
        entries = []
        if self.smoking_status:
            smoking_status = self.smoking_status.display
            if self.smoking_packyears is not None:
                smoking_status += f' ({round(self.smoking_packyears,1)} pack-years)'
            if self.smoking_quited is not None:
                smoking_status += f' ({round(self.smoking_quited.year,1)} years ago)'
            entries.append(f'Smoking: {smoking_status}')
        if self.alcohol_consumption:
            entries.append(f'Alcohol: {self.alcohol_consumption.display}')
        if self.night_sleep is not None:
            entries.append(f'Sleep: {round(self.night_sleep.hour,2)} h/night')
        if self.recreational_drugs.exists():
            entries.append(f'Recreational drugs: {", ".join([drug.display for drug in self.recreational_drugs.all()])}')
        if self.exposures.exists():
            entries.append(f'Exposures: {", ".join([exposure.display for exposure in self.exposures.all()])}')
        return ' \n'.join(entries)
