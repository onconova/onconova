from measurement.base import MeasureBase, BidimensionalMeasure

from measurement.measures import Mass, Volume as VolumeBase

class Unit(MeasureBase):
    STANDARD_UNIT = 'kIU'
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