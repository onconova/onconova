
from django.db import models
from django.contrib.postgres.fields import DateRangeField
from pop.terminology.fields import CodedConceptField
from pop.terminology.models import CodedConcept
from enum import Enum 

class OptionsEnum(str, Enum):
    OPTIONA = 'optionA'
    OPTIONB = 'optionB'

class MockCodedConcept(CodedConcept):
    pass
    
class MockModel(models.Model):
    id_field = models.CharField(primary_key=True)
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
