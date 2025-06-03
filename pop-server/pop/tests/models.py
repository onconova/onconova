
from django.db import models
import pghistory
from django.contrib.postgres.fields import DateRangeField
from pop.terminology.fields import CodedConceptField
from pop.terminology.models import CodedConcept
from pop.core.models import BaseModel
from enum import Enum 

class OptionsEnum(models.TextChoices):
    OPTIONA = 'optionA'
    OPTIONB = 'optionB'

class MockCodedConcept(CodedConcept):
    pass
    
class UntrackedMockBaseModel(BaseModel):    
    pass

@pghistory.track()
class MockBaseModel(BaseModel):    
    pass

class MockModel(models.Model):
    id = models.CharField(primary_key=True)
    str_field = models.CharField(null=True)
    date_field = models.DateField(null=True)
    datetime_field = models.DateTimeField(null=True)
    int_field = models.IntegerField(null=True)
    float_field = models.FloatField(null=True)
    enum_field = models.CharField(null=True, choices=OptionsEnum)
    bool_field = models.BooleanField(null=True)
    period_field = DateRangeField(null=True)
    float_field = models.FloatField(null=True)
    coded_concept_field = CodedConceptField(null=True, _to=MockCodedConcept, terminology=None)
    multi_coded_concept_field = CodedConceptField(null=True, _to=MockCodedConcept, terminology=None, multiple=True)
