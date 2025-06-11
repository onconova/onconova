from ninja import Schema, Field
from pydantic import AliasChoices

class Measure(Schema):
    """
    Represents a measurable quantity with its value and unit.

    Attributes:
        value (float): The numerical value of the measure.
        unit (str): The unit in which the value is expressed.
    """

    value: float = Field(
        title="Value",
        description="The numerical value of the measure.",
        alias="value"
    )
    unit: str = Field(
        title="Unit",
        description="The unit of measurement (e.g., 'kg', 'm', 'ml').",
        alias="unit"
    )


class MeasureConversion(Schema):
    """
    Represents a measure value and its intended conversion to a new unit.

    Attributes:
        value (float): The numerical value of the measure.
        unit (str): The unit of the measure.
        newUnit (str): The new unit to convert the measure to.
    """

    value: float = Field(
        title="Value",
        description="The numerical value of the measure to be converted.",
        alias="value"
    )
    unit: str = Field(
        title="Original Unit",
        description="The current unit of the measure.",
        alias="unit"
    )
    newUnit: str = Field(
        title="New Unit",
        description="The target unit to convert the measure into.",
        alias="new_unit",
        validation_alias=AliasChoices("newUnit", "new_unit")
    )