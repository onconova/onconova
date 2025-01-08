from measurement.base import MeasureBase, BidimensionalMeasure
from measurement.measures import Mass, Volume as VolumeBase

def get_measurement(measure, value, unit=None, original_unit=None):
    unit = unit or measure.STANDARD_UNIT

    m = measure(**{unit: value})
    if original_unit:
        m.unit = original_unit
    if isinstance(m, BidimensionalMeasure):
        m.reference.value = 1
    return m


class Unit(MeasureBase):
    STANDARD_UNIT = 'IU'
    UNITS = {
        'IU': 1.0,
    }
    ALIAS = {
        'international unit': 'IU',
    }
    SI_UNITS = ['IU']

class Substance(MeasureBase):
    STANDARD_UNIT = 'mol'
    UNITS = {
        'mol': 1.0,
    }
    ALIAS = {
        'moles': 'mol',
    }
    SI_UNITS = ['mol']

class MultipleOfMedian(MeasureBase):
    STANDARD_UNIT = 'M.o.M'
    UNITS = {
        'M.o.M': 1.0,
    }
    ALIAS = {
        'multiple_of_median': 'M.o.M',
    }
    

class RadiationDose(MeasureBase):
    STANDARD_UNIT = 'Gy'
    UNITS = {
        'Gy': 1.0,
    }
    ALIAS = {
        'gray': 'Gy',
    }
    SI_UNITS = ['Gy']
    

class Time(MeasureBase):

    """ Time measurements (generally for multidimensional measures).

    Please do not use this for handling durations of time unrelated to
    measure classes -- python's built-in datetime module has much better
    functionality for handling intervals of time than this class provides.

    """
    STANDARD_UNIT = 's'
    UNITS = {
        's': 1.0,
        'min': 60.0,
        'hour': 3600.0,
        'day': 86400.0,
        'week': 604800.0,
        'month': 26282880,
        'year': 31536000.0,
    }
    ALIAS = {
        'second': 's',
        'sec': 's', 
        'minute': 'min',
        'hour': 'hour',
        'day': 'day',
        'week': 'week',
        'month': 'month',
        'year': 'year',
    }
    SI_UNITS = ['s']

    
class Volume(VolumeBase):
    STANDARD_UNIT = 'l'
    UNITS = {
        'us_g': 3.78541,
        'us_qt': 0.946353,
        'us_pint': 0.473176,
        'us_cup': 0.236588,
        'us_oz': 2.9574e-2,
        'us_tbsp': 1.4787e-2,
        'us_tsp': 4.9289e-3,
        'cubic_millimeter': 0.000001,
        'cubic_centimeter': 0.001,
        'cubic_decimeter':  0.001,
        'cubic_meter': 1000,
        'l': 1,
        'cubic_foot': 28.3168,
        'cubic_inch': 1.6387e-2,
        'imperial_g': 4.54609,
        'imperial_qt': 1.13652,
        'imperial_pint': 0.568261,
        'imperial_oz': 2.8413e-2,
        'imperial_tbsp': 1.7758e-3,
        'imperial_tsp': 5.9194e-3,
    }
    SI_UNITS = ['l']


class Area(VolumeBase):
    STANDARD_UNIT = 'square_meter'
    UNITS = {
        'square_millimeter': 1000000,
        'square_centimeter': 10000,
        'square_decimeter':  100,
        'square_meter': 1,
        'square_foot': 10.76391,
        'square_inch': 1550.003,
        'square_yard': 1.19599,
    }
    
class Fraction(MeasureBase):
    STANDARD_UNIT = '%'
    UNITS = {
        '%': 1.0,
        'pph': 1.0,
        'ppm': 10000,
        'ppb': 10000000,
        'ppt': 10000000000,
    }
    ALIAS = {
        '%': 'percentage',
        'pph': 'parts_per_hundreth',
        'ppm': 'parts_per_million',
        'ppb': 'parts_per_billion',
        'ppt': 'parts_per_trillion',
    }


class MassConcentration(BidimensionalMeasure):
    PRIMARY_DIMENSION = Mass
    REFERENCE_DIMENSION = Volume

class SubstanceConcentration(BidimensionalMeasure):
    PRIMARY_DIMENSION = Substance
    REFERENCE_DIMENSION = Volume

class ArbitraryConcentration(BidimensionalMeasure):
    PRIMARY_DIMENSION = Unit
    REFERENCE_DIMENSION = Volume

class MassPerArea(BidimensionalMeasure):
    PRIMARY_DIMENSION = Mass
    REFERENCE_DIMENSION = Area


class MassPerTime(BidimensionalMeasure):
    PRIMARY_DIMENSION = Mass
    REFERENCE_DIMENSION = Time

class VolumePerTime(BidimensionalMeasure):
    PRIMARY_DIMENSION = Volume
    REFERENCE_DIMENSION = Time

class MassConcentrationPerTime(BidimensionalMeasure):
    PRIMARY_DIMENSION = MassConcentration
    REFERENCE_DIMENSION = Time

class MassPerAreaPerTime(BidimensionalMeasure):
    PRIMARY_DIMENSION = MassPerArea
    REFERENCE_DIMENSION = Time