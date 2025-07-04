from datetime import date, datetime
from typing import Optional, List, Dict, Union, Any
from uuid import UUID
from enum import Enum
from ninja import Schema
from psycopg.types.range import Range as PostgresRange
from pydantic import Field, model_validator, AliasChoices
from ninja_extra.schemas import NinjaPaginationResponseSchema


class Paginated(NinjaPaginationResponseSchema):
    """
    Standard paginated response schema.
    """

    pass


class ModifiedResource(Schema):
    """
    Represents a resource that was modified in the system.
    """

    id: UUID = Field(description="Unique identifier of the modified resource.")
    description: Optional[str] = Field(
        default=None,
        description="A human-readable description of the modified resource.",
    )


class CodedConcept(Schema):
    """
    Represents a concept coded in a controlled terminology system.
    """

    code: str = Field(
        description="Unique code within a coding system that identifies a concept."
    )
    system: str = Field(
        description="Canonical URL of the code system defining the concept."
    )
    display: Optional[str] = Field(
        default=None, description="Human-readable description of the concept."
    )
    version: Optional[str] = Field(
        default=None, description="Release version of the code system, if applicable."
    )
    synonyms: Optional[List[str]] = Field(
        default=None,
        description="List of synonyms or alternative representations of the concept.",
    )
    properties: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional properties associated with the concept."
    )


class Range(Schema):
    """
    Represents a numeric or comparable range between two values.
    """

    start: Optional[Union[int, float]] = Field(
        description="The lower bound of the range."
    )
    end: Optional[Union[int, float]] = Field(
        default=None,
        description="The upper bound of the range. If not provided, assumed unbounded.",
    )

    @model_validator(mode="before")
    def parse_range(cls, obj):
        """
        Accepts either a tuple, PostgresRange, or dict-like object.
        """
        range_obj = obj._obj
        if isinstance(range_obj, str):
            start, end = range_obj.strip("()[]").split(",")
            return {"start": start, "end": end}
        elif isinstance(range_obj, tuple):
            return {"start": range_obj[0], "end": range_obj[1]}
        elif isinstance(range_obj, PostgresRange):
            return {"start": range_obj.lower, "end": range_obj.upper}
        return obj

    def to_range(self) -> Union[tuple, PostgresRange]:
        """
        Converts this Range schema into a Python tuple.
        """
        return (self.start, self.end)


class Period(Schema):
    """
    Represents a time period between two dates.
    """

    start: Optional[date] = Field(
        default=None, description="The start date of the period."
    )
    end: Optional[date] = Field(default=None, description="The end date of the period.")

    @model_validator(mode="before")
    def parse_period(cls, obj):
        """
        Accepts either a tuple, PostgresRange, or dict-like object.
        """
        period_obj = obj._obj
        if isinstance(period_obj, str):
            start, end = period_obj.strip("()[]").split(",")
            return {"start": start, "end": end}
        elif isinstance(period_obj, tuple):
            return {"start": period_obj[0], "end": period_obj[1]}
        elif isinstance(period_obj, PostgresRange):
            return {"start": period_obj.lower, "end": period_obj.upper}
        return obj

    def to_range(self) -> tuple:
        """
        Converts this Period schema into a Python tuple of dates.
        """
        return (self.start, self.end)
