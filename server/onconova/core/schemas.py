from datetime import date, datetime
from typing import Any, Dict, Generic, List, TypeVar, Union

from ninja import Schema
from psycopg.types.range import Range as PostgresRange
from pydantic import Field, field_validator, model_validator

from onconova.core.anonymization import AnonymizationMixin
from onconova.core.serialization.base import BaseSchema
from onconova.core.measures.schemas import Measure
from onconova.core.types import Nullable, UUID, Username

T = TypeVar("T")

__all__ = (
    "BaseSchema",
    "MetadataMixin",
    "MetadataAnonymizationMixin",
    "Paginated",
    "ModifiedResource",
    "Measure",
    "CodedConcept",
    "Range",
    "Period"
)

class MetadataMixin:
    
    id: UUID = Field(
        ..., description='Unique identifier of the resource (UUID v4).', title='Id'
    )
    description: str = Field(
        ..., description='Human-readable description', title='Description'
    )
    createdAt: Nullable[datetime] = Field(
        None, description='Date-time when the resource was created', title='Created at'
    )
    updatedAt: Nullable[datetime] = Field(
        None,
        description='Date-time when the resource was last updated',
        title='Updated at',
    )
    createdBy: Nullable[Username] = Field(
        None,
        description='Username of the user who created the resource',
        title='Created by',
    )
    updatedBy: Nullable[List[Username]] = Field(
        None,
        description='Usernames of the users who have updated the resource',
        title='Updated by',
    )

class MetadataAnonymizationMixin(MetadataMixin, AnonymizationMixin):
    pass
    
class Paginated(Schema, Generic[T]):
    """
    A generic paginated response schema.

    Attributes:
        count (int): The total number of items available.
        items (List[T]): The list of items on the current page.

    Methods:
        validate_items(cls, value: Any) -> Any:
            Ensures that the 'items' attribute is a list. Converts to list if necessary.
    """
    count: int
    items: List[T]

    @field_validator("items", mode="before")
    def validate_items(cls, value: Any) -> Any:
        if value is not None and not isinstance(value, list):
            value = list(value)
        return value

class ModifiedResource(Schema):
    """
    Represents a resource that was modified in the system.

    Attributes:
        id (UUID): Unique identifier (UUID4) of the modified resource.
        description (Optional[str]): A human-readable description of the modified resource.
    """

    id: UUID = Field(
        title="ID", description="Unique identifier (UUID4) of the modified resource."
    )
    description: Nullable[str] = Field(
        default=None,
        title="Description",
        description="A human-readable description of the modified resource.",
    )

class CodedConcept(Schema):
    """
    Represents a concept coded in a controlled terminology system.

    Attributes:
        code (str): Unique code within a coding system that identifies a concept.
        system (str): Canonical URL of the code system defining the concept.
        display (Optional[str]): Human-readable description of the concept.
        version (Optional[str]): Release version of the code system, if applicable.
        synonyms (Optional[List[str]]): List of synonyms or alternative representations of the concept.
        properties (Optional[Dict[str, Any]]): Additional properties associated with the concept.
    """

    code: str = Field(
        title="Code",
        description="Unique code within a coding system that identifies a concept.",
    )
    system: str = Field(
        title="System",
        description="Canonical URL of the code system defining the concept.",
    )
    display: Nullable[str] = Field(
        title="Display",
        default=None,
        description="Human-readable description of the concept.",
    )
    version: Nullable[str] = Field(
        title="Version",
        default=None,
        description="Release version of the code system, if applicable.",
    )
    synonyms: Nullable[List[str]] = Field(
        default=None,
        title="Synonyms",
        description="List of synonyms or alternative representations of the concept.",
    )
    properties: Nullable[Dict[str, Any]] = Field(
        title="Properties",
        default=None,
        description="Additional properties associated with the concept.",
    )

class Range(Schema):
    """
    Range schema for representing a numeric interval with optional bounds.

    Attributes:
        start (Nullable[int | float]): The lower bound of the range.
        end (Nullable[int | float]): The upper bound of the range. If not provided, the range is considered unbounded.
    """

    start: Nullable[int | float] = Field(
        title="Start", description="The lower bound of the range."
    )
    end: Nullable[int | float] = Field(
        default=None,
        title="End",
        description="The upper bound of the range. If not provided, assumed unbounded.",
    )

    @model_validator(mode="before")
    def parse_range(cls, obj):
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
    Schema representing a time period with optional start and end dates.

    Attributes:
        start (Nullable[date]): The start date of the period. Can be None.
        end (Nullable[date]): The end date of the period. Can be None.
    """

    start: Nullable[date] = Field(
        default=None, title="Start", description="The start date of the period."
    )
    end: Nullable[date] = Field(
        default=None, title="End", description="The end date of the period."
    )

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
