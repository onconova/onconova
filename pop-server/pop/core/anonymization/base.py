from datetime import date, datetime, timedelta
from typing import Union, List, Tuple, Optional, Self
from django.conf import settings
from pydantic import Field, model_validator
from pydantic.dataclasses import dataclass
from pydantic.fields import PrivateAttr
from pop.core.utils import hash_to_range 
from pop.core.schemas.others import Period

ANONYMIZED_STRING = '*************'

def anonymize_date(original_date, key):
    timeshift = hash_to_range(key, secret=settings.ANONYMIZATION_SECRET_KEY, low=-90, high=90)
    return original_date + timedelta(days=abs(timeshift)) if timeshift>0 else original_date - timedelta(days=abs(timeshift))

def anonymize_value(value, key):
    # Anonymize date/time fields by introducing a hash-based time-shift
    if isinstance(value, (datetime, date)):
        anonymized_value = anonymize_date(value, key)
    # Anonymize string fields by replacing by a placeholder 
    elif isinstance(value, (Period)):
        anonymized_value = Period(start=anonymize_date(value.start, key) if value.start else None, end=anonymize_date(value.end, key) if value.end else None)
    # Anonymize string fields by replacing by a placeholder 
    elif isinstance(value, (str)):
        anonymized_value = ANONYMIZED_STRING
    else:
        # Otherwise raise an error 
        raise NotImplementedError(f'Could not anonymize value of type {type(value)}')
    return anonymized_value

@dataclass
class AnonymizationConfig:
    fields: Union[List[str], Tuple[str]]
    key: str

class AnonymizationMixin:
    
    anonymized: bool = Field(default=False, title='Is anonymized', description='Whether the data has been anonymized')
    
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

    