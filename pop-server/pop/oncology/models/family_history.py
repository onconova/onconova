import pghistory 

from django.db import models
from django.utils.translation import gettext_lazy as _

from pop.core.models import BaseModel 
from pop.oncology.models import PatientCase 
import pop.terminology.fields as termfields 
import pop.terminology.models as terminologies 


@pghistory.track()
class FamilyHistory(BaseModel):

    case = models.ForeignKey(
        verbose_name = _('Patient case'),
        help_text = _("Indicates the case of the patient who's family's history is being recorded"),
        to = PatientCase,
        related_name = 'family_histories',
        on_delete = models.CASCADE,
    )
    date = models.DateField(
        verbose_name = _('Assessment date'),
        help_text=_("Clinically-relevant date at which the patient's family history was assessed and recorded."),
    ) 
    relationship = termfields.CodedConceptField(
        verbose_name = _('Relationship'),
        help_text = _("Relationship to the patient"),
        terminology = terminologies.FamilyMemberType,  
    ) 
    had_cancer = models.BooleanField(
        verbose_name = _('Had cancer'),
        help_text = _('Whether the family member has a history of cancer'),
    ) 
    contributed_to_death = models.BooleanField(
        verbose_name = _('Contributed to death'),
        help_text = _('Whether the cancer contributed to the cause of death of the family member'),
        null = True, blank = True,
    ) 
    onset_age = models.PositiveSmallIntegerField(
        verbose_name = _('Onset age'),
        help_text = _("Age at which the family member's cancer manifested"),
        null = True, blank = True,
    ) 
    topography = termfields.CodedConceptField(
        verbose_name = _('Topography'), 
        help_text = _("Estimated or actual topography of the family member's cancer"),
        terminology = terminologies.CancerTopography,
        null=True,blank=True,
    )
    morphology = termfields.CodedConceptField(
        verbose_name = _('Morphology'),
        help_text = _("Morphology of the family member's cancer (if known)"),
        terminology = terminologies.CancerMorphology,
        null=True,blank=True,
    )
    
    @property
    def description(self):
        if self.had_cancer:
            return f"{self.relationship} with {self.topography.display.lower().replace(', nos','')} cancer"
        else: 
            return f"{self.relationship} without history of cancer"