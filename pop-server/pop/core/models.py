import random 
from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timesince
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class BaseModel(models.Model):
    auto_id = models.BigAutoField(
        verbose_name=_('Database ID'),
        help_text=_('Automated incremental database identifier'),
        primary_key=True,
        editable=False,
    )
    id = models.CharField(
        max_length=64,
        unique=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    created_by = models.ForeignKey(
        help_text=_('The user who created the original data'),
        to=UserModel,
        on_delete=models.SET_NULL,
        null=True,
    )
    updated_by = models.ManyToManyField(
        help_text=_('The user(s) who updated the data since its creation'),
        to=UserModel,
        related_name='+'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.pk and not self.id:
            self.id = self._generate_unique_id()

    class Meta:
        abstract = True
 
    @property
    def description(self):
        raise NotImplementedError

    def __str__(self):
        return self.description

    @property
    def last_updated(self):
        return self.updated_at
 
    @property
    def timesince_last_edit(self):
        return timesince.timesince(self.modifiedAt)
 
    @property
    def timesince_created(self):
        return timesince.timesince(self.createdAt)
 
    @property
    def hours_since_last_created(self):
        delta = datetime.now() - self.createdAt
        return delta.total_seconds() / (60 * 60)
 
    @property
    def days_since_last_created(self):
        return self.hours_since_last_created/24

    @property
    def date_label(self):
        for field in self._meta.fields:
            if isinstance(field,models.PeriodField): 
                if getattr(self, field.name + '_start') or getattr(self, field.name + '_end'):
                    start_date, end_date = 'Unknown','Ongoing'
                    if getattr(self, field.name + '_start'):
                        start_date = getattr(self, field.name + '_start').strftime('%b %-d, %Y')
                    if getattr(self, field.name + '_end'):
                        end_date = getattr(self, field.name + '_end').strftime('%b %-d, %Y')
                    date = f"{start_date} - {end_date}"
            elif isinstance(field,models.DateTimeField) or isinstance(field,models.DateField): 
                if getattr(self, field.name):
                    date = getattr(self, field.name)      
                    date = date.strftime('%b %-d, %Y')
        if date: 
            if hasattr(self, 'report'):    
                if self.report.first():
                    report = self.report.first().testName   
                    date += f' | {report}'   
        return date
    
    
    def _generate_unique_id(self):
        def _generate_random_id():
            digit = lambda N: ''.join([str(random.randint(1,9)) for _ in range(N)])
            return f'POP-{self.__class__.__name__}-{digit(4)}-{digit(3)}-{digit(2)}'
        # Generate random digits
        new_id = _generate_random_id()
        # Check for ID clashes in the database
        while self.__class__.objects.filter(id=new_id).exists():
            new_id = _generate_random_id()
        # Set the ID for the patient
        return new_id

