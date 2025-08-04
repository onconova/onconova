from measurement.base import (
    MeasureBase,
    BidimensionalMeasure as BidimensionalMeasureBase,
)
from measurement.measures import Mass, Volume as VolumeBase, Distance
from sympy import S, Symbol

class Measure(MeasureBase):

    @property
    def unit(self):
        return self._default_unit

    @unit.setter
    def unit(self, value):
        aliases = self.get_aliases()
        laliases = self.get_lowercase_aliases()
        units = self.get_units()
        unit = None
        if value in self.UNITS:
            unit = value
        elif value in aliases:
            unit = aliases[unit]
        elif value in units:
            unit = value
        elif value.lower() in units:
            unit = value.lower()
        elif value.lower() in laliases:
            unit = laliases[value.lower]
        if not unit:
            raise ValueError("Invalid unit %s" % value)
        self._default_unit = unit

    def __str__(self):
        value = getattr(self, self._default_unit)
        return f"{round(value,2)} {self.unit}"


class BidimensionalMeasure(BidimensionalMeasureBase):

    def get_units(self): 
        return [
            f"{primary}__{reference}"
            for primary in list(self.PRIMARY_DIMENSION.get_units())
            for reference in  list(self.REFERENCE_DIMENSION.get_units())
        ]
        
    @property
    def unit(self):
        return "%s__%s" % (
            self.primary.unit,
            self.reference.unit,
        )

    @unit.setter
    def unit(self, value):
        primary, reference = value.rsplit("__", 1)
        reference_units = self.REFERENCE_DIMENSION.get_units()
        if reference != self.reference.unit:
            reference_chg = (
                reference_units[self.reference.unit] / reference_units[reference]
            )
            self.primary.standard = self.primary.standard / reference_chg
        self.primary.unit = primary
        self.reference.unit = reference

    def _get_unit_parts(self, measure_string):
        if measure_string in self.ALIAS:
            measure_string = self.ALIAS[measure_string]
        try:
            primary_unit, reference_unit = measure_string.rsplit("__", 1)
        except:
            primary_unit, reference_unit = super()._get_unit_parts(measure_string)
        return primary_unit, reference_unit

    def __getattr__(self, measure_string):
        # Fixes bug when accessing class meta attributes (i.e. allows measure objects to be used in Django TestCase instances)
        if measure_string.startswith("__"):
            return super().__getattribute__(measure_string)
        return super().__getattr__(measure_string)

    def __str__(self):
        if isinstance(self.primary, (Measure, MeasureBase)):
            primary_unit = self.primary.get_aliases().get(
                self.primary.unit, self.primary.unit
            )
        else:
            primary_unit = self.primary
        if isinstance(self.reference, (Measure, MeasureBase)):
            reference_unit = self.reference.get_aliases().get(
                self.reference.unit, self.reference.unit
            )
        else:
            reference_unit = self.reference
        return f"{round(self.primary.value,2)} {primary_unit}/{reference_unit}"


def get_measurement(value, measure=None, unit=None, original_unit=None):
    """
    Creates a measurement object with the specified value and unit.

    Args:
        measure (Measure): The measure class to be instantiated.
        value (float): The numerical value of the measurement.
        unit (str, optional): The unit of the measurement. Defaults to the measure's standard unit.
        original_unit (str, optional): The original unit of the measurement, if different from `unit`.

    Returns:
        Measure: An instance of the measure class with the specified value and unit.
    """
    if not measure and not unit and not original_unit: 
        raise ValueError('Either measure, original_unit, or unit must be provided.')
    if not measure and (unit or original_unit): 
        from pop.core.measures import ALL_MEASURES
        measure = next((measure for measure in ALL_MEASURES if (unit or original_unit) in measure.get_units()))
    # If unit is not specified use the class' standard unit
    unit = unit or measure.STANDARD_UNIT
    # Construct measurement
    m = measure(**{unit: value})
    if original_unit:
        m.unit = original_unit
    if isinstance(m, BidimensionalMeasure):
        m.reference.value = 1
    return m


def get_measure_db_value(value, unit):
    measurement = get_measurement(value=value, unit=unit)
    return getattr(measurement, measurement.STANDARD_UNIT)


class Temperature(Measure):
    SU = Symbol("kelvin")
    STANDARD_UNIT = "kelvin"
    UNITS = {
        "celsius": SU - S(273.15),
        "fahrenheit": (SU - S(273.15)) * S("9/5") + 32,
        "kelvin": 1.0,
    }
    ALIAS = {
        "celsius": "°C",
        "fahrenheit": "°F",
        "kelvin": "K",
    }


class Unit(Measure):
    """
    International Unit (IU) of measurement.

    Notes
    -----
    The International Unit (IU) is a unit of measurement that is used to quantify the activity of certain substances, such as vitamins and hormones. It is defined as the amount of the substance that is needed to produce a specific biological effect.

    Examples
    --------
    >>> unit = Unit(10)
    >>> print(unit)
    10 IU
    """

    STANDARD_UNIT = "IU"
    UNITS = {
        "IU": 1.0,
    }
    ALIAS = {
        "IU": "IU",
    }
    SI_UNITS = ["IU"]


class Substance(Measure):
    """
    A measurement of substance.

    The substance is a base physical quantity and the International System of Units (SI) defines the mole (mol) as its unit.

    Examples
    --------
    >>> substance = Substance(1)
    >>> print(substance)
    1 mol

    >>> substance = Substance(1, 'mol')
    >>> print(substance)
    1 mol

    >>> substance = Substance(1, 'gram')
    >>> print(substance)
    0.016042773999999998 mol
    """

    STANDARD_UNIT = "mol"
    UNITS = {
        "mol": 1.0,
    }
    ALIAS = {
        "moles": "mol",
    }
    SI_UNITS = ["mol"]


class MultipleOfMedian(Measure):
    """
    A measure of quantity as a multiple of the median.

    Notes
    -----
    The Multiple of Median (M.o.M) is a measure of quantity that is
    relative to the median value of a specific population. It is
    commonly used to express the value of a particular quantity in
    terms of the median value of the population.

    Examples
    --------
    >>> mom = MultipleOfMedian(10)
    >>> print(mom)
    10 M.o.M

    >>> mom = MultipleOfMedian(10, 'M.o.M')
    >>> print(mom)
    10 M.o.M
    """

    STANDARD_UNIT = "multiple_of_median"
    UNITS = {
        "multiple_of_median": 1.0,
    }
    ALIAS = {
        "multiple_of_median": "M.o.M",
    }


class Pressure(Measure):
    """
    A measure of pressure.

    The Pressure class is used for representing and converting pressure
    values in various units. The standard unit is Pascal (Pa).

    Examples
    --------
    >>> pressure = Pressure(Pa=100)
    >>> print(pressure)
    100 Pa

    >>> pressure.convert_to('atm')
    0.0009869250513319517 atm
    """

    STANDARD_UNIT = "Pa"
    UNITS = {
        "Pa": 1,
        "atm": 9.869250513319517e-6,
        "mmHg": 0.00750062,
        "psi": 0.000145038,
        "bar": 1.0000018082621e-5,
        "Torr": 0.0075006303913072412681,
    }
    ALIAS = {
        "Pascal": "Pa",
        "atmospheres": "atm",
        "milimetre of mercury": "mmHg",
        "pund per square inch": "psi",
        "Bar": "bar",
        "torr ": "Torr",
    }
    SI_UNITS = ["Pa"]


class RadiationDose(Measure):
    """
    A measure of radiation dose.

    The RadiationDose class is used for representing and converting radiation
    dose values in various units. The standard unit is Gray (Gy).

    Examples
    --------
    >>> radiation_dose = RadiationDose(Gy=10)
    >>> print(radiation_dose)
    10 Gy

    >>> radiation_dose.convert_to('Rad')
    100 Rad
    """

    STANDARD_UNIT = "Gy"
    UNITS = {
        "Gy": 1.0,
    }
    ALIAS = {
        "gray": "Gy",
    }
    SI_UNITS = ["Gy"]


class Time(Measure):
    """
    A measure of time.

    The Time class is used for representing and converting time values in
    various units. The standard unit is seconds (s).

    Examples
    --------
    >>> time = Time(s=10)
    >>> print(time)
    10 s

    >>> time.convert_to('min')
    0.166666667 min
    """

    STANDARD_UNIT = "s"
    UNITS = {
        "s": 1.0,
        "min": 60.0,
        "hour": 3600.0,
        "day": 86400.0,
        "week": 604800.0,
        "month": 26282880,
        "year": 31536000.0,
    }
    ALIAS = {
        "second": "s",
        "sec": "s",
        "minute": "min",
        "hour": "hours",
        "day": "days",
        "week": "weeks",
        "month": "months",
        "year": "years",
    }
    SI_UNITS = ["s"]


class Volume(VolumeBase):
    """
    Represents a measurement of volume.

    The Volume class is used for representing and converting volume
    values in various units. The standard unit is liter (l).

    Examples:
        >>> volume = Volume(l=1)
        >>> print(volume)
        1 l

        >>> volume.convert_to('cubic_meter')
        0.001 cubic_meter
    """

    STANDARD_UNIT = "l"
    UNITS = {
        "us_g": 3.78541,
        "us_qt": 0.946353,
        "us_pint": 0.473176,
        "us_cup": 0.236588,
        "us_oz": 2.9574e-2,
        "us_tbsp": 1.4787e-2,
        "us_tsp": 4.9289e-3,
        "cubic_millimeter": 0.000001,
        "cubic_centimeter": 0.001,
        "cubic_decimeter": 0.001,
        "cubic_meter": 1000,
        "l": 1,
        "cubic_foot": 28.3168,
        "cubic_inch": 1.6387e-2,
        "imperial_g": 4.54609,
        "imperial_qt": 1.13652,
        "imperial_pint": 0.568261,
        "imperial_oz": 2.8413e-2,
        "imperial_tbsp": 1.7758e-3,
        "imperial_tsp": 5.9194e-3,
    }
    SI_UNITS = ["l"]


class Area(Measure):
    """
    Represents an area measurement.

    The Area class is used for representing and converting area values
    in various units. The standard unit is square meter (m^2).

    Examples:
        >>> area = Area(square_meter=1)
        >>> print(area)
        1 m^2

        >>> area.convert_to('square_foot')
        10.76391 square_foot

    """

    STANDARD_UNIT = "square_meter"
    UNITS = {
        "square_millimeter": 1000000,
        "square_centimeter": 10000,
        "square_decimeter": 100,
        "square_meter": 1,
        "square_foot": 10.76391,
        "square_inch": 1550.003,
        "square_yard": 1.19599,
    }
    ALIAS = {
        "square_millimeter": "mm²",
        "square_centimeter": "cm²",
        "square_decimeter": "dm²",
        "square_meter": "m²",
        "square_foot": "ft²",
        "square_inch": "in²",
        "square_yard": "yd²",
    }


class Fraction(Measure):
    """
    Represents a fraction measurement.

    The Fraction class is used for representing and converting fraction values
    in various units. The standard unit is percentage (%).

    Examples:
        >>> fraction = Fraction(percentage=1)
        >>> print(fraction)
        1.0 %

        >>> fraction.convert_to('parts_per_million')
        10000.0 parts_per_million

    """

    STANDARD_UNIT = "%"
    UNITS = {
        "%": 1.0,
        "pph": 1.0,
        "ppm": 10000,
        "ppb": 10000000,
        "ppt": 10000000000,
    }
    ALIAS = {
        "%": "percentage",
        "pph": "parts_per_hundreth",
        "ppm": "parts_per_million",
        "ppb": "parts_per_billion",
        "ppt": "parts_per_trillion",
    }


class MassConcentration(BidimensionalMeasure):
    """
    Represents a measurement of mass concentration.

    The MassConcentration class is used for representing and converting mass
    concentration values in various units. The standard unit is gram per liter
    (g/l).

    Examples:
        >>> mass_concentration = MassConcentration(g_per_l=1)
        >>> print(mass_concentration)
        1 g/l

        >>> mass_concentration.convert_to('mg_per_dl')
        100.0 mg/dl

    """

    PRIMARY_DIMENSION = Mass
    REFERENCE_DIMENSION = Volume


class SubstanceConcentration(BidimensionalMeasure):
    """
    Represents a measurement of substance concentration.

    The SubstanceConcentration class is used for representing and converting
    substance concentration values in various units. The standard unit is mole
    per liter (mol/l).

    Examples:
        >>> substance_concentration = SubstanceConcentration(mol_per_l=1)
        >>> print(substance_concentration)
        1 mol/l

        >>> substance_concentration.convert_to('mmol_per_l')
        1000.0 mmol/l

    """

    PRIMARY_DIMENSION = Substance
    REFERENCE_DIMENSION = Volume


class ArbitraryConcentration(BidimensionalMeasure):
    """
    Represents a measurement of arbitrary concentration.

    The ArbitraryConcentration class is used for representing and converting
    arbitrary concentration values in various units.

    Examples:
        >>> arbitrary_concentration = ArbitraryConcentration(Unit=1)
        >>> print(arbitrary_concentration)
        1 Unit/Volume

        >>> arbitrary_concentration.convert_to('another_unit')
        X another_unit
    """

    PRIMARY_DIMENSION = Unit
    REFERENCE_DIMENSION = Volume


class MassPerArea(BidimensionalMeasure):
    """
    Represents a measurement of mass per area.

    The MassPerArea class is used for representing and converting mass per area
    values in various units. The standard unit is gram per square meter (g/m^2).

    Examples:
        >>> mass_per_area = MassPerArea(g_per_m2=1)
        >>> print(mass_per_area)
        1 g/m^2

        >>> mass_per_area.convert_to('mg_per_cm2')
        10.0 mg/cm^2

    """

    PRIMARY_DIMENSION = Mass
    REFERENCE_DIMENSION = Area


class MassPerTime(BidimensionalMeasure):
    """
    Represents a measurement of mass per time.

    The MassPerTime class is used for representing and converting mass per time
    values in various units. The standard unit is gram per second (g/s).

    Examples:
        >>> mass_per_time = MassPerTime(g_per_s=1)
        >>> print(mass_per_time)
        1 g/s

        >>> mass_per_time.convert_to('mg_per_min')
        60000.0 mg/min

    """

    PRIMARY_DIMENSION = Mass
    REFERENCE_DIMENSION = Time


class VolumePerTime(BidimensionalMeasure):
    """
    Represents a measurement of volume per time.

    The VolumePerTime class is used for representing and converting volume per time
    values in various units. The standard unit is cubic meter per second (m^3/s).

    Examples:
        >>> volume_per_time = VolumePerTime(m3_per_s=1)
        >>> print(volume_per_time)
        1 m^3/s

        >>> volume_per_time.convert_to('l_per_min')
        60000.0 l/min

    """

    PRIMARY_DIMENSION = Volume
    REFERENCE_DIMENSION = Time


class MassConcentrationPerTime(BidimensionalMeasure):
    """
    Represents a measurement of mass concentration per time.

    The MassConcentrationPerTime class is used for representing and converting
    mass concentration per time values in various units. The standard unit is
    gram per liter per second (g/l/s).

    Examples:
        >>> mass_concentration_per_time = MassConcentrationPerTime(g_per_l_per_s=1)
        >>> print(mass_concentration_per_time)
        1 g/l/s

        >>> mass_concentration_per_time.convert_to('mg_per_dl_per_min')
        6000.0 mg/dl/min

    """

    PRIMARY_DIMENSION = MassConcentration
    REFERENCE_DIMENSION = Time


class MassPerAreaPerTime(BidimensionalMeasure):
    """
    Represents a measurement of mass per area per time.

    The MassPerAreaPerTime class is used for representing and converting mass
    per area per time values in various units. The standard unit is gram per
    square meter per second (g/m^2/s).

    Examples:
        >>> mass_per_area_per_time = MassPerAreaPerTime(g_per_m2_per_s=1)
        >>> print(mass_per_area_per_time)
        1 g/m^2/s

        >>> mass_per_area_per_time.convert_to('mg_per_cm2_per_min')
        10.0 mg/cm^2/min

    """

    PRIMARY_DIMENSION = MassPerArea
    REFERENCE_DIMENSION = Time
