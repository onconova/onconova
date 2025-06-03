from datetime import date, datetime, timedelta
from  typing import Union, List, Tuple, Optional, Self
from django.conf import settings
from pydantic import Field, model_validator
from pydantic.dataclasses import dataclass
from pydantic.fields import PrivateAttr
from pop.core.utils import hash_to_range 

ANONYMIZED_STRING = '*************'


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
        
        for field in self.__anonymization_fields__:
            value = getattr(self, field)
            
            # If the field has no value, no need to anonymize
            if not value:
                continue
            
            # Anonymize date/time fields by introducing a hash-based time-shift
            if isinstance(value, (datetime, date)):
                timeshift = hash_to_range(self.__anonymization_key__, secret=settings.ANONYMIZATION_SECRET_KEY, low=-90, high=90)
                anonymized_value = value + timedelta(days=abs(timeshift)) if timeshift>0 else value - timedelta(days=abs(timeshift))

            # Anonymize string fields by replacing by a placeholder 
            elif isinstance(value, (str)):
                anonymized_value = ANONYMIZED_STRING
            setattr(self, field, anonymized_value)    
        return self

    