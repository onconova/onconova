from typing import List 
from ninja_extra import route, api_controller, ControllerBase

from measurement.base import MeasureBase, BidimensionalMeasure

from pop.core.security import XSessionTokenAuth
from pop.core.measures.schemas import MeasureConversion, Measure
from pop.core.measures import measures

@api_controller(
    '/measures', 
    auth=[XSessionTokenAuth()], 
    tags=['Measures'],  
)
class MeasuresController(ControllerBase):

    @route.get(
        path="/{measureName}/units", 
        operation_id='getMeasureUnits',
        response={
            200: List[str],
            404: None
        }, 
    )
    def get_measure_units(self, measureName: str):
        measure = getattr(measures, measureName, None)
        if measure is None:
            return 404, None
        units = []
        if issubclass(measure, MeasureBase):
            units = list(measure.get_units())
        elif issubclass(measure, BidimensionalMeasure):
            primaries = list(measure.PRIMARY_DIMENSION.get_units())
            references = list(measure.REFERENCE_DIMENSION.get_units())
            units = [
                f'{primary}__{reference}' for primary in primaries for reference in references
            ]
        return 200, units

    @route.get(
        path="/{measureName}/units/default", 
        operation_id='getMeasureDefaultUnits',
        response={
            200: str,
            404: None
        }, 
    )
    def get_measure_default_units(self, measureName: str):
        measure = getattr(measures, measureName, None)
        if measure is None:
            return 404, None
        return 200, measure.STANDARD_UNIT


    @route.post(
        path="/{measureName}/units/conversion", 
        operation_id='convertUnits',
        response={
            200: Measure,
            404: None
        }, 
    )
    def convert_units(self, measureName: str, payload: MeasureConversion):
        measureClass = getattr(measures, measureName, None)
        if measureClass is None:
            return 404, None
        measure = measureClass(**{payload.unit: payload.value})
        converted_value = getattr(measure, payload.new_unit)
        return 200, Measure(unit=payload.new_unit, value=converted_value)