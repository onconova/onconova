
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator 

from pop.core.models import BaseModel 
from pop.oncology.models import PatientCase
import pop.terminology.models as terminologies

ECOG_INTEPRETATION = {
    0: 'LA9622-7', 1: 'LA9623-5', 2: 'LA9624-3', 
    3: 'LA9625-0', 4: 'LA9626-8', 5: 'LA9627-6',
}

KARNOFSKY_INTEPRETATION = {
    0: 'LA9627-6', 10: 'LA29184-1', 20: 'LA29183-3', 
    30: 'LA29182-5', 40: 'LA29181-7', 50: 'LA29180-9', 
    60: 'LA29179-1', 70: 'LA29178-3', 80: 'LA29177-5', 
    90: 'LA29176-7', 100: 'LA29175-9',
}

class PerformanceStatus(BaseModel):
 
    case = models.ForeignKey(
        verbose_name = _('Patient case'),
        help_text = _("Indicates the case of the patient who's performance status is assesed"),
        to = PatientCase,
        related_name = 'performance_status',
        on_delete = models.CASCADE,
    )
    date = models.DateField(
        verbose_name = _('Assessment date'),
        help_text = _("Clinically-relevant date at which the performance score was performed and recorded."),
    ) 
    ecog_score = models.PositiveSmallIntegerField(
        verbose_name = _('ECOG Score'),
        help_text = _("ECOG Performance Status Score"), 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        blank = True, null=True,
    )
    karnofsky_score = models.PositiveSmallIntegerField(
        verbose_name = _('Karnofsky Score'),
        help_text = _("Karnofsky Performance Status Score"), 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank = True, null=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(ecog_score__isnull=False) | 
                          models.Q(karnofsky_score__isnull=False),
                name='at_least_one_score_must_be_set'
            )
        ]

    @property 
    def ecog_interpretation(self):
        if self.ecog_score is None:
            return None 
        interpretation_code = ECOG_INTEPRETATION.get(self.ecog_score)
        return terminologies.ECOGPerformanceStatusInterpretation.objects.filter(code=interpretation_code).first()
        
    @property 
    def karnofsky_interpretation(self):
        if self.karnofsky_score is None:
            return None 
        interpretation_code = KARNOFSKY_INTEPRETATION.get(self.karnofsky_score)
        return terminologies.KarnofskyPerformanceStatusInterpretation.objects.filter(code=interpretation_code).first()
        
    @property
    def description(self):
        if self.ecog_score is not None:
            return f'ECOG: ({self.ecog_score})'
        elif self.karnofsky_score is not None:
            return f'Karnofsky ({self.karnofsky_score})'
        
    def convert_karnofsky_to_ecog(self):
        """
        Reference
        ---------
        [1] Oken et al., Am. J. Clin. Oncol. 5(6):649-655, 1982.
        """
        if self.ecog_score is not None:
            return self.ecog_score
        if self.karnofsky_score == 100:
            return 0
        elif self.karnofsky_score >= 80:
            return 1
        elif self.karnofsky_score >= 60:
            return 2
        elif self.karnofsky_score >= 40:
            return 3
        elif self.karnofsky_score >= 20:
            return 4
        elif self.karnofsky_score == 0:
            return 5