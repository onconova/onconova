from typing import List 
from ninja_extra import route, api_controller, ControllerBase
from ninja_jwt.authentication import JWTAuth

from measurement.base import MeasureBase, BidimensionalMeasure

from pop.core.measures.schemas import MeasureConversionSchema, MeasureSchema
import pop.core.measures.measures as measures


@api_controller(
    '/measures', 
    auth=[JWTAuth()], 
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
            units = list(measure.UNITS.keys())
        elif issubclass(measure, BidimensionalMeasure):
            primaries = list(measure.PRIMARY_DIMENSION.UNITS.keys())
            references = list(measure.REFERENCE_DIMENSION.UNITS.keys())
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
            200: MeasureSchema,
            404: None
        }, 
    )
    def convert_units(self, measureName: str, payload: MeasureConversionSchema):
        measureClass = getattr(measures, measureName, None)
        if measureClass is None:
            return 404, None
        measure = measureClass(**{payload.unit: payload.value})
        converted_value = getattr(measure, payload.new_unit)
        return 200, MeasureSchema(unit=payload.new_unit, value=converted_value)