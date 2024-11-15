from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timesince
from django.conf import settings

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
        db_column='created_at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at'
    )
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='+',
        editable=False,
    )
    modified_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='+',
        editable=False,
    )


    class Meta:
        abstract = True
 
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
        delta = now() - self.createdAt
        return delta.total_seconds() / (60 * 60)
 
    @property
    def days_since_last_created(self):
        return self.hours_since_last_created/24

    @property
    def date_label(self):
        for field in self._meta.fields:
            if isinstance(field,PeriodField): 
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
    
    def _generate_random_id(self):
        return f'POP-{self.__class__.__name__}-{digit(4)}-{digit(3)}-{digit(2)}'
    
    def save(self, *args, **kwargs):
        # If an ID has not been manually specified, add an automated one
        if not self.id:
            # Generate random digits
            new_id = self._generate_random_id()
            # Check for ID clashes in the database
            while CancerPatient.objects.filter(id=new_id).exists():
                new_id = self._generate_random_id()
            # Set the ID for the patient
            self.id = new_id
        return super().save(*args, **kwargs)
