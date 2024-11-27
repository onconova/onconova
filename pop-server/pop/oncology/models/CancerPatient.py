import random 
import string

from django.db import models 
from django.db.models import F, Func, ExpressionWrapper, Case, When, Value
from django.utils.translation import gettext_lazy as _

from pop.core.models import BaseModel 

import pop.terminology.fields as termfields 
import pop.terminology.models as terminologies 

class CancerPatientManager(models.Manager):
    def get_queryset(self):
        """
        Annotate the queryset with a database-level age computation.

        Age is computed using PostgreSQL's built-in AGE and EXTRACT functions.
        The computation is done on the database side, so it is both fast and
        queriable. The age is computed as the difference in years between the
        birthdate and either the date of death or the current date if the
        patient is alive.
        """
        return super().get_queryset().annotate(
            # Add patient age computed at database-level (fast and queriable)
            _age=ExpressionWrapper(
                Func(
                    Func(
                        Case(
                            When(date_of_death__isnull=False, then=F('date_of_death')),
                            default=Func(function='NOW'),  # Use current date if date_of_death is NULL
                        ),
                        F('birthdate'),
                        function='AGE'
                    ),
                    function="EXTRACT",
                    template="EXTRACT(YEAR FROM %(expressions)s)"
                ),
                output_field=models.IntegerField()
            )
        )
        
class CancerPatient(BaseModel):
    """
    A patient who has been diagnosed with or is receiving medical 
    treatment for a malignant growth or tumor
    """ 
    objects = CancerPatientManager()
    
    pseudoidentifier = models.CharField(
        verbose_name = _('Pseudoidentifier'),
        help_text = _("Pseudoidentifier of the patient"),
        max_length = 40, 
        unique = True,
        editable = False,
    )
    race = termfields.CodedConceptField(
        verbose_name = _('Race'),
        help_text = _("Race of the patient"),
        terminology = terminologies.RaceCategory,    
        null = True, 
        blank = True,    
    )
    birthsex = termfields.CodedConceptField(
        verbose_name = _('Birth sex'),
        help_text = _("Sex assigned at birth"),
        terminology = terminologies.BirthSex,
        blank = True, 
        null = True,
    )
    gender_identity = termfields.CodedConceptField(
        verbose_name = _('Gender identity'),
        terminology = terminologies.GenderIdentity,
        null = True, 
        blank = True,        
    )
    gender = termfields.CodedConceptField(
        verbose_name = _('Gender'),
        help_text = _("Gender for administrative purposes"),
        terminology = terminologies.AdministrativeGender, 
    )
    birthdate = models.DateField(
        verbose_name = _('Date of birth'),
        help_text = _('Date of birth'),
    )
    is_deceased = models.GeneratedField(
        verbose_name = _('Is deceased'),
        help_text = _("Indicates if the individual is deceased or not (determined automatically based on existence of a date of death)"),
        expression = Case(
            When(date_of_death__isnull = False, then = Value(True)),  # Deceased if `date_of_death` is not null
            default = Value(False),  # Not deceased otherwise
            output_field = models.BooleanField(),
        ),
        output_field = models.BooleanField(),
        db_persist = True,
    )
    date_of_death = models.DateField(
        verbose_name = _('Date of death'),
        help_text = _("Date on which the patient was declared dead"),
        null=True, blank=True,
    )
    
    @property
    def age(self):
        """
        Calculate the age of the patient based on the birthdate and current date
        or date of death, if available. The age is computed at the database level.
        """
        return self.__class__.objects.filter(pk=self.pk).values('_age')[0]['_age']
    
    def _generate_random_id(self):
        """
        Generates a random identifier string for a patient record.
        
        The format of the string is 'X.NNN.YYY.ZZ', where 'X' is a random uppercase letter, 
        'NNN' is a random 3-digit number, 'YYY' is a random 3-digit number, and 'ZZ' is a random 2-digit number.
        
        This function is used to generate a unique identifier for a patient record if one is not 
        specified when a patient record is created.
        """
        digit = lambda N: ''.join([str(random.randint(1,9)) for _ in range(N)])
        return f'{random.choice(string.ascii_letters).upper()}.{digit(4)}.{digit(3)}.{digit(2)}'
    
    def save(self, *args, **kwargs):
        # If an ID has not been manually specified, add an automated one
        """
        If an ID has not been manually specified, add an automated one.
        
        When saving a patient record, if no ID is specified, this method will generate
        a random one and check it against existing records in the database. If a conflict
        is found, it will generate a new ID and check it again. This ensures that the ID
        is unique.
        
        The ID is generated using the `_generate_random_id` method.
        """
        if not self.pseudoidentifier:
            # Generate random digits
            new_pseudoidentifier = self._generate_random_id()
            # Check for ID clashes in the database
            while CancerPatient.objects.filter(id=new_pseudoidentifier).exists():
                new_pseudoidentifier = self._generate_random_id()
            # Set the ID for the patient
            self.pseudoidentifier = new_pseudoidentifier
        return super().save(*args, **kwargs)
    