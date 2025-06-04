from datetime import date, datetime, timedelta
from typing import Union, List, Tuple, Optional, Self
from django.conf import settings
from pydantic import Field, model_validator
from pydantic.dataclasses import dataclass
from pydantic.fields import PrivateAttr
from pop.core.utils import hash_to_range, is_datetime, is_period 
from pop.core.schemas.others import Period
from pop.core.types import Age, AgeBin

ANONYMIZED_STRING = '*************'

def anonymize_date(original_date, key):
    timeshift = hash_to_range(key, secret=settings.ANONYMIZATION_SECRET_KEY, low=-90, high=90)
    return original_date + timedelta(days=abs(timeshift)) if timeshift>0 else original_date - timedelta(days=abs(timeshift))

def anonymize_age(age: Age) -> AgeBin:
    bins = [
        (AgeBin.SUB_20,       (None, 19)),
        (AgeBin.AGE_20_24,    (20, 24)),
        (AgeBin.AGE_25_30,    (25, 30)),
        (AgeBin.AGE_30_34,    (31, 34)),
        (AgeBin.AGE_35_40,    (35, 40)),
        (AgeBin.AGE_40_44,    (41, 44)),
        (AgeBin.AGE_45_50,    (45, 50)),
        (AgeBin.AGE_50_54,    (51, 54)),
        (AgeBin.AGE_55_60,    (55, 60)),
        (AgeBin.AGE_60_64,    (61, 64)),
        (AgeBin.AGE_65_70,    (65, 70)),
        (AgeBin.AGE_70_74,    (71, 74)),
        (AgeBin.AGE_75_80,    (75, 80)),
        (AgeBin.AGE_80_84,    (81, 84)),
        (AgeBin.AGE_85_90,    (85, 90)),
        (AgeBin.OVER_90,      (91, None)),
    ]
    for age_bin, (low, high) in bins:
        if (low is None or age >= low) and (high is None or age <= high):
            return age_bin
    raise ValueError(f"Age {age} is out of valid range")

def anonymize_value(value, key):
    # Anonymize date/time fields by introducing a hash-based time-shift
    if isinstance(value, (datetime, date)):
        anonymized_value = anonymize_date(value, key)
    elif isinstance(value, (str)) and is_datetime(value,'%Y-%m-%d'):
        anonymized_value = anonymize_date(datetime.strptime(value, '%Y-%m-%d').date(), key)
    # Anonymize string fields by replacing by a placeholder 
    elif isinstance(value, (Period)):
        anonymized_value = Period(start=anonymize_date(value.start, key) if value.start else None, end=anonymize_date(value.end, key) if value.end else None)
    elif isinstance(value, (str)) and is_period(value,'%Y-%m-%d'):
        period_start_string, period_end_string = value.strip('()[]').split(',')
        anonymized_value = Period(start=anonymize_date(datetime.strptime(period_start_string, '%Y-%m-%d'), key) or None, end=anonymize_date(datetime.strptime(period_end_string, '%Y-%m-%d') , key) or None)
        anonymized_value = f'{anonymized_value.start} to {anonymized_value.end}'
    # Anonymize string fields by replacing by a placeholder 
    elif isinstance(value, (str)):
        anonymized_value = ANONYMIZED_STRING
    # Anonymize string fields by replacing by a placeholder 
    elif isinstance(value, (Age)):
        anonymized_value = anonymize_age(value)
    else:
        # Otherwise raise an error 
        raise NotImplementedError(f'Could not anonymize value of type {type(value)}')
    return anonymized_value

@dataclass
class AnonymizationConfig:
    fields: Union[List[str], Tuple[str]]
    key: str

class AnonymizationMixin:
    
    anonymized: bool = Field(default=False, title='Is anonymized', description='Whether the data has been anonymized', validate_default=True)
    
    # Anonymization metadata    
    __anonymization_fields__: Union[List[str], Tuple[str]] = ()
    __anonymization_key__: Optional[str]
    
    @model_validator(mode='after')
    def anonymize_data(self) -> Self:
        # If schema is not set to be anonymized, just return current validated state
        if not self.anonymized:
            return self        
        # Go over all fields configured to be anonymized
        for field in self.__anonymization_fields__:
            value = getattr(self, field)
            # If the field has no value, no need to anonymize
            if not value:
                continue
            # Set the anonymized value
            setattr(self, field, anonymize_value(value, self.__anonymization_key__))    
        return self

    