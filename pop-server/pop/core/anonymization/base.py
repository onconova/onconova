from datetime import date, datetime, timedelta
from typing import Union, List, Tuple, Optional, Self
from django.conf import settings
from pydantic import Field, model_validator
from pydantic.dataclasses import dataclass
from pydantic.fields import PrivateAttr
from pop.core.utils import hash_to_range, is_datetime, is_period 
from pop.core.schemas.others import Period
from pop.core.types import Age, AgeBin

REDACTED_STRING = '*************'
AVERAGE_MONTH = 30.436875
MAX_DATE_SHIFT = round(6*AVERAGE_MONTH)

def anonymize_by_redacting_string(original_value: str):
    return REDACTED_STRING

def anonymize_clinically_relevant_date(original_date: date | datetime | str, case_id: str):
    if isinstance(original_date, str):
        try:
            original_date = datetime.strptime(original_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Unrecognized date format: {original_date}")
    # Compute random timeshift of +-6 months based on a hash of the case ID
    timeshift = hash_to_range(case_id, secret=settings.ANONYMIZATION_SECRET_KEY, low=-MAX_DATE_SHIFT, high=MAX_DATE_SHIFT)
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


def anonymize_personal_date(original_date: str):
    if isinstance(original_date, datetime) or isinstance(original_date, date):
        return original_date.year
    elif isinstance(original_date, str):
        try:
            parsed_date = datetime.fromisoformat(original_date)
            return parsed_date.year
        except ValueError:
            try:
                parsed_date = datetime.strptime(original_date, "%Y-%m-%d")
                return parsed_date.year
            except ValueError:
                raise ValueError(f"Unrecognized date format: {original_date}")
    else:
        raise TypeError(f"Unsupported type: {type(original_date)}")

def anonymize_value(value, case_id):
    # Anonymize date/time fields by introducing a hash-based time-shift
    if isinstance(value, (datetime, date)) or (isinstance(value, (str)) and is_datetime(value,'%Y-%m-%d')):
        anonymized_value = anonymize_clinically_relevant_date(value, case_id)
    # Anonymize string fields by replacing by a placeholder 
    elif isinstance(value, (Period)):
        anonymized_value = Period(
            start=anonymize_clinically_relevant_date(value.start, case_id) if value.start else None, 
            end=anonymize_clinically_relevant_date(value.end, case_id) if value.end else None
        )
    elif isinstance(value, (str)) and is_period(value,'%Y-%m-%d'):
        period_start_string, period_end_string = value.strip('()[]').split(',')
        anonymized_value = Period(
            start=anonymize_clinically_relevant_date(period_start_string, case_id) or None, 
            end=anonymize_clinically_relevant_date(period_end_string, case_id) or None
        )
        anonymized_value = f'{anonymized_value.start} to {anonymized_value.end}'
    # Anonymize string fields by replacing by a placeholder 
    elif isinstance(value, str):
        anonymized_value = anonymize_by_redacting_string(value)
    # Anonymize string fields by replacing by a placeholder 
    elif isinstance(value, Age):
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

    