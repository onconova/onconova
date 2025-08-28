from enum import Enum

import pghistory
from django.contrib.postgres.fields import DateRangeField, IntegerRangeField
from django.db import models

from onconova.core.models import BaseModel
from onconova.terminology.fields import CodedConceptField
from onconova.terminology.models import CodedConcept


class OptionsEnum(models.TextChoices):
    OPTIONA = "optionA"
    OPTIONB = "optionB"


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
    range_field = IntegerRangeField(null=True)
    float_field = models.FloatField(null=True)
    coded_concept_field = CodedConceptField(
        null=True, _to=MockCodedConcept, terminology=None
    )
    multi_coded_concept_field = CodedConceptField(
        null=True, _to=MockCodedConcept, terminology=None, multiple=True
    )
