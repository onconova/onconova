from typing import List

from measurement.base import BidimensionalMeasure, MeasureBase
from ninja_extra import ControllerBase, api_controller, route

from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.measures import measures
from onconova.core.measures.schemas import Measure, MeasureConversion


@api_controller(
    "/measures",
    auth=[XSessionTokenAuth()],
    tags=["Measures"],
)
class MeasuresController(ControllerBase):
    """
    API controller for handling measure-related operations.
    """

    @route.get(
        path="/{measureName}/units",
        operation_id="getMeasureUnits",
        response={200: List[str], 404: None},
    )
    def get_measure_units(self, measureName: str):
        """
        Retrieves the available units for a specified measure.
        """
        measure = getattr(measures, measureName, None)
        if measure is None:
            return 404, None
        units = []
        units = list(measure.get_units())
        return 200, units

    @route.get(
        path="/{measureName}/units/default",
        operation_id="getMeasureDefaultUnits",
        response={200: str, 404: None},
    )
    def get_measure_default_units(self, measureName: str):
        """
        Retrieves the default unit for a specified measure.
        """
        measure = getattr(measures, measureName, None)
        if measure is None:
            return 404, None
        return 200, measure.STANDARD_UNIT

    @route.post(
        path="/{measureName}/units/conversion",
        operation_id="convertUnits",
        response={200: Measure, 404: None},
    )
    def convert_units(self, measureName: str, payload: MeasureConversion):
        """
        Converts a measurement from one unit to another using the specified measure class.
        """
        measureClass = getattr(measures, measureName, None)
        if measureClass is None:
            return 404, None
        measure = measureClass(**{payload.unit: payload.value})
        converted_value = getattr(measure, payload.newUnit)
        return 200, Measure(unit=payload.newUnit, value=converted_value)
