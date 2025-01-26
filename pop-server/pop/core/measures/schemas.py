
from ninja import Schema
from pydantic import ConfigDict

class MeasureSchema(Schema):
    """
    Represents a measure value with its unit.

    Attributes:
        value (float): The numerical value of the measure.
        unit (str): The unit of the measure.
    """
    value: float
    unit: str

    # Schema config
    model_config = ConfigDict(
        title='Measure',
    )


class MeasureConversionSchema(Schema):
    """
    Represents a measure value to be converted to another unit.

    Attributes:

        value (float): The numerical value of the measure.
        unit (str): The unit of the measure.
        new_unit (str): The new unit to convert the measure to.
    """
    value: float
    unit: str
    new_unit: str

    # Schema config
    model_config = ConfigDict(
        title='MeasureConversion',
    )
