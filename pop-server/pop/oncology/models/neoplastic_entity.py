import pghistory

from django.db import models
from django.utils.translation import gettext_lazy as _

from pop.core.models import BaseModel 
from pop.oncology.models import PatientCase 
import pop.terminology.fields as termfields 
import pop.terminology.models as terminologies 
    
PRIMARY = 'primary'
METASTATIC = 'metastatic'
LOCAL_RECURRENCE = 'local_recurrence'
REGIONAL_RECURRENCE = 'regional_recurrence'

class NeoplasticEntityRelationship(models.TextChoices):
    PRIMARY = PRIMARY
    METASTATIC = METASTATIC
    LOCAL_RECURRENCE = LOCAL_RECURRENCE
    REGIONAL_RECURRENCE = REGIONAL_RECURRENCE 

@pghistory.track()
class NeoplasticEntity(BaseModel):
    
    case = models.ForeignKey(
        verbose_name = _('Patient case'),
        help_text = _("Indicates the case of the patient who's neoplasm(s) are recorded"),
        to = PatientCase,
        related_name = 'neoplastic_entities',
        on_delete = models.CASCADE,
    )
    relationship = models.CharField(
        verbose_name = _("Neoplastic relationship"),
        help_text = _("Relationship linking secondary and recurrent tumors to their primary origin or for distinguishing between different phases of the disease."),
        max_length = 30,
        choices = NeoplasticEntityRelationship,
    )
    related_primary = models.ForeignKey(
        verbose_name = _("Related primary neoplasm"),
        help_text = _("Reference to the primary neoplasm of which the neoplasm(s) originated from."),
        to = "self",
        related_name ='recurrences',
        on_delete=models.CASCADE,
        null = True, blank = True,
    )
    assertion_date = models.DateField(
        verbose_name = _('Assertion date'),
        help_text = _("The date on which the existence of the neoplasm(s) was first asserted or acknowledged"),
    ) 
    topography = termfields.CodedConceptField(
        verbose_name = _('Topography'), 
        help_text = _('Anatomical location of the neoplasm(s)'),
        terminology = terminologies.CancerTopography,
    )
    morphology = termfields.CodedConceptField(
        verbose_name = _('Morphology'),
        help_text = _("Describes the cell type of the tumor and its biologic activity, in other words, the characteristics of the tumor itself"),
        terminology = terminologies.CancerMorphology,
    )
    differentitation = termfields.CodedConceptField(
        verbose_name = _('Differentiation'),
        help_text = _("Morphologic differentitation characteristics of the neoplasm(s)"),
        terminology = terminologies.HistologyDifferentiation,
        null = True, blank = True,
    )
    laterality = termfields.CodedConceptField(
        verbose_name=_('Laterality'),
        help_text=_('Laterality qualifier for the location of the neoplasm(s)'),
        terminology = terminologies.LateralityQualifier,
        null = True, blank = True,
    )
    
    @property
    def description(self):
        """
        Human-readable description of the neoplastic entity
        """
        # Get core information
        morphology = self.morphology.display.lower().replace(', nos','').replace(', metastatic','')
        topography = self.topography.display.lower().replace(', nos','') .replace(', metastatic','')       
        # If the neoplasm has specified laterality, add it to the topography
        if self.laterality:
            laterality = self.laterality.display.lower().replace(' (qualifier value)','')
            topography = f'{laterality} {topography}'
        # If the neoplasm has a specified differentations, categorize it into grading
        if self.differentitation:
            diff_code = self.differentitation.code
            grading = 'Low-grade' if diff_code in ['1','2'] \
                        else 'High-grade' if diff_code in ['3','4'] \
                            else self.differentitation.display.split(',')[-1]
            morphology = f'{grading} {morphology}'
        # Adapt the word composition to whether the topography is described by a single word or not
        if len(topography.split()) == 1: 
            description = f'{topography} {morphology}'
        else:
            description = f'{morphology} of the {topography}'
        # Add the relationship/role of the neoplasm      
        description = f'{self.relationship} {description}' 
        return description.capitalize()
    
                
    class Meta:
        verbose_name = "Neoplastic Entity"
        verbose_name_plural  = "Neoplastic Entities"
        constraints = [
            models.CheckConstraint(
                condition = models.Q(relationship='primary', related_primary=None) | ~models.Q(relationship='primary'),
                name = 'primary_cannot_have_a_related_primary',
                violation_error_message = 'A primary neoplasm cannot have a related primary',
            )
        ]
        
        
        
