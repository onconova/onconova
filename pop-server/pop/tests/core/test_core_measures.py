from unittest import TestCase
from parameterized import parameterized 
from pop.core.measures import measures as m

class TestMeasures(TestCase):
    
    @parameterized.expand([
        (m.Unit),
        (m.Temperature),
        (m.Mass),
        (m.Substance),
        (m.MultipleOfMedian),
        (m.Pressure),
        (m.RadiationDose),
        (m.Time),
        (m.Volume),
        (m.Fraction),
        (m.MassConcentration),
        (m.SubstanceConcentration),
        (m.ArbitraryConcentration),
        (m.MassPerArea),
        (m.MassPerTime),
        (m.VolumePerTime),
        (m.MassConcentrationPerTime),
        (m.MassPerAreaPerTime),
    ],name_func = lambda fcn,idx,param:  f'{fcn.__name__}_{idx}_{list(param)[0][0].__name__}'
    )   
    def test_measure(self, measure):
        standard_unit = measure.STANDARD_UNIT
        measurement = measure(**{standard_unit: 1})
        displayed_decimals = len(str(measurement).split(' ',1)[0].split('.',1)[-1])
        self.assertTrue(displayed_decimals < 3, f'Measure "{str(measurement)}" not truncating decimals correctly ({displayed_decimals} shown)')
        