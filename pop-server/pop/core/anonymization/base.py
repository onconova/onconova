from datetime import date, datetime, timedelta
from typing import Any, Callable, ClassVar, Dict, List, Tuple, Type, Union

from django.conf import settings
from pop.core.types import Age, AgeBin
from pop.core.utils import hash_to_range, is_datetime, is_period
from pydantic import BaseModel, Field, model_validator
from pydantic.dataclasses import dataclass

REDACTED_STRING = "*************"
AVERAGE_MONTH = 30.436875
MAX_DATE_SHIFT = round(6 * AVERAGE_MONTH)


def anonymize_by_redacting_string(original_value: Any) -> str:
    """
    Anonymizes a string by returning a redacted string.

    Args:
        original_value (str): The value to be anonymized.

    Returns:
        str: The redacted string value.
    """
    return REDACTED_STRING


def anonymize_clinically_relevant_date(
    original_date: date | datetime | str,
    case_id: str,
) -> date | datetime:
    """
    Anonymizes a date by shifting it by a random amount between -6 and 6 months.

    Args:
        original_date (Union[date, datetime, str]): The date to be anonymized.
        case_id (str): The case ID used to generate the random timeshift.

    Returns:
        Union[date, datetime]: The anonymized date.
    """
    if isinstance(original_date, str):
        try:
            original_date = datetime.strptime(original_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Unrecognized date format: {original_date}")
    # Compute random timeshift of +-6 months based on a hash of the case ID
    timeshift = hash_to_range(
        case_id,
        secret=settings.ANONYMIZATION_SECRET_KEY,
        low=-MAX_DATE_SHIFT,
        high=MAX_DATE_SHIFT,
    )
    return (
        original_date + timedelta(days=abs(timeshift))
        if timeshift > 0
        else original_date - timedelta(days=abs(timeshift))
    )


def anonymize_age(age: Age) -> AgeBin:
    """Anonymize an age value by mapping it to its corresponding age bin.

    Args:
        age (Age): The age value to be anonymized.

    Returns:
        AgeBin: The anonymized age bin.
    """
    bins = [
        (AgeBin.SUB_20, (0, 19)),
        (AgeBin.AGE_20_24, (20, 24)),
        (AgeBin.AGE_25_29, (25, 29)),
        (AgeBin.AGE_30_34, (30, 34)),
        (AgeBin.AGE_35_39, (35, 39)),
        (AgeBin.AGE_40_44, (40, 44)),
        (AgeBin.AGE_45_49, (45, 49)),
        (AgeBin.AGE_50_54, (50, 54)),
        (AgeBin.AGE_55_59, (55, 59)),
        (AgeBin.AGE_60_64, (60, 64)),
        (AgeBin.AGE_65_69, (65, 69)),
        (AgeBin.AGE_70_74, (70, 74)),
        (AgeBin.AGE_75_79, (75, 79)),
        (AgeBin.AGE_80_84, (80, 84)),
        (AgeBin.AGE_85_89, (85, 89)),
        (AgeBin.OVER_90, (90, 150)),
    ]
    for age_bin, (low, high) in bins:
        if (low is None or age >= low) and (high is None or age <= high):
            return age_bin
    raise ValueError(f"Age {age} is out of valid range")


def anonymize_personal_date(original_date: datetime | date | str) -> date:
    """
    Anonymize a date by returning only the year.

    Args:
        original_date (Union[datetime, date, str]): The date to be anonymized.

    Returns:
        date: The year of the anonymized date with month and day set to 1.
    """
    if isinstance(original_date, (datetime, date)):
        return datetime(original_date.year, 1, 1).date()
    elif isinstance(original_date, str):
        try:
            parsed_date = datetime.fromisoformat(original_date)
            return datetime(parsed_date.year, 1, 1).date()
        except ValueError:
            try:
                parsed_date = datetime.strptime(original_date, "%Y-%m-%d")
                return datetime(parsed_date.year, 1, 1).date()
            except ValueError:
                raise ValueError(f"Unrecognized date format: {original_date}")
    else:
        raise TypeError(f"Unsupported type: {type(original_date)}")


def anonymize_value(value: Any, case_id: str) -> Any:
    """
    Anonymize a value by replacing it with a suitable placeholder.

    This function anonymizes date/time fields by introducing a hash-based time-shift,
    anonymizes string fields by replacing by a placeholder, and anonymizes age fields by binning the age.

    Args:
        value (Any): The value to be anonymized.
        case_id (str): The case ID to be used for hash-based anonymization.

    Returns:
        Any: The anonymized value.
    """
    from pop.core.schemas import Period

    # Anonymize date/time fields by introducing a hash-based time-shift
    if isinstance(value, (datetime, date)) or (
        isinstance(value, (str)) and is_datetime(value, "%Y-%m-%d")
    ):
        anonymized_value = anonymize_clinically_relevant_date(value, case_id)
    # Anonymize string fields by replacing by a placeholder

    elif isinstance(value, (Period)):
        anonymized_value = Period(
            start=(
                anonymize_clinically_relevant_date(value.start, case_id)
                if value.start
                else None
            ),
            end=(
                anonymize_clinically_relevant_date(value.end, case_id)
                if value.end
                else None
            ),
        )
    elif isinstance(value, (str)) and is_period(value, "%Y-%m-%d"):
        period_start_string, period_end_string = value.strip("()[]").split(",")
        anonymized_value = Period(
            start=anonymize_clinically_relevant_date(period_start_string, case_id)
            or None,
            end=anonymize_clinically_relevant_date(period_end_string, case_id) or None,
        )
        anonymized_value = f"{anonymized_value.start} to {anonymized_value.end}"
    # Anonymize string fields by replacing by a placeholder
    elif isinstance(value, str):
        anonymized_value = anonymize_by_redacting_string(value)
    # Anonymize age fields by binning the age
    elif isinstance(value, Age):
        anonymized_value = anonymize_age(value)
    else:
        # Otherwise raise an error
        raise NotImplementedError(f"Could not anonymize value of type {type(value)}")
    return anonymized_value


@dataclass
class AnonymizationConfig:
    fields: Union[List[str], Tuple[str]]
    key: str
    functions: Dict[str, Callable] = Field(default_factory=dict)


class AnonymizationMixin:
    """
    Mixin class for automatic anonymization of specified model fields after validation.

    Attributes:
        anonymized (bool): Flag indicating whether anonymization should be applied.
        __anonymization_fields__ (Tuple[str, ...]): Class-level tuple listing the field names to anonymize.
        __anonymization_key__ (Optional[str]): Optional key used in the anonymization process.
        __anonymization_functions__ (Dict[str, Callable]): Optional mapping of field names to custom anonymization functions.

    Methods:
        anonymize_data(): Pydantic model validator that anonymizes the configured fields if 'anonymized' is True.
        anonymize_value(value): Instance method for anonymizing a single value, can be overridden by subclasses.
        __post_anonymization_hook__(): Hook method for subclasses to implement post-anonymization actions.
    """

    anonymized: bool = Field(
        default=False,
        title="Is anonymized",
        description="Whether the data has been anonymized",
        validate_default=True,
    )

    # Anonymization metadata
    __anonymization_fields__: ClassVar[Tuple[str, ...]] = ()
    __anonymization_key__: ClassVar[str | None] = None
    __anonymization_functions__: ClassVar[Dict[str, Callable]] = {}

    @classmethod
    def _setup(
        cls,
        model_class: type,
        config: AnonymizationConfig | None = None,
    ):
        if config:
            model_class.__anonymization_fields__ = (
                *config.fields,
                *config.functions.keys(),
            )
            model_class.__anonymization_key__ = config.key
            model_class.__anonymization_functions__ = config.functions

    @model_validator(mode="after")
    def anonymize_data(self) -> Any:
        # If schema is not set to be anonymized, just return current validated state
        if not self.anonymized:
            return self

        # Go over all fields configured to be anonymized
        for field in self.__anonymization_fields__:

            # If the field has no value, no need to anonymize
            value = getattr(self, field)
            if not value:
                continue

            # Use field-specific anonymizer if available, else fallback
            anonymizer = self.__anonymization_functions__.get(
                field, self.anonymize_value
            )
            anonymized_value = anonymizer(value)

            # Set the anonymized value
            setattr(self, field, anonymized_value)

        # Call post-anonymization hook for subclasses
        self.__post_anonymization_hook__()

        return self

    def anonymize_value(self, value):
        """Hook for per-instance anonymization logic."""
        return anonymize_value(value, self.__anonymization_key__ or "")

    def __post_anonymization_hook__(self):
        """
        Hook method for subclasses to implement additional actions after anonymization.
        Default implementation does nothing.
        """
        pass
