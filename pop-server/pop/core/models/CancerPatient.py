from django.db import models 
from django.utils.translation import gettext_lazy as _
import pop.core.models.fields as custom
import random 
import string
from .BaseModel import BaseModel 

class CancerPatient(BaseModel):
    """
    A patient who has been diagnosed with or is receiving medical treatment for a malignant growth or tumor
    """ 
    pseudoidentifier = models.CharField(
        verbose_name=_('Pseudoidentifier'),
        help_text=_("Pseudoidentifier of the patient"),
        max_length=40, 
        unique=True,
        editable=False,
    )
    race = custom.CodedConceptField(
        verbose_name=_('Race'),
        help_text=_("Race of the patient"),
        valueset='RaceCategory',    
        null=True, blank=True,    
    )
    birthsex = custom.CodedConceptField(
        verbose_name=_('Birth sex'),
        help_text=_("Sex assigned at birth"),
        valueset='BirthSex',
        blank=True, null=True,
    )
    gender_identity = custom.CodedConceptField(
        valueset='GenderIdentity',
        null=True, blank=True,        
    )
    gender = custom.CodedConceptField(
        verbose_name=_('Gender'),
        help_text=_("Gender for administrative purposes"),
        valueset='AdministrativeGender', 
    )
    birthdate = models.DateField(
        verbose_name=_('Date of birth'),
        help_text=_('Date of birth'),
    )
    id_deceased = models.BooleanField(
        verbose_name=_('Is deceased'),
        help_text=_("Indicates if the individual is deceased or not"),
        null=True,
    )
    
    def _generate_random_id(self):
        digit = lambda N: ''.join([str(random.randint(1,9)) for _ in range(N)])
        return f'{random.choice(string.ascii_letters)}{digit(4)}.{digit(3)}.{digit(2)}'
    
    def save(self, *args, **kwargs):
        # If an ID has not been manually specified, add an automated one
        if not self.pseudoidentifier:
            # Generate random digits
            new_pseudoidentifier = self._generate_random_id()
            # Check for ID clashes in the database
            while CancerPatient.objects.filter(id=new_pseudoidentifier).exists():
                new_pseudoidentifier = self._generate_random_id()
            # Set the ID for the patient
            self.pseudoidentifier = new_pseudoidentifier
        return super().save(*args, **kwargs)
