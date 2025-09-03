import warnings

from django.db.models import FloatField
from django.utils.translation import gettext_lazy as _
from measurement import measures
from measurement.base import BidimensionalMeasure, MeasureBase, BidimensionalMeasure

from .measures import get_measurement

class MeasurementField(FloatField):
    """
    A custom Django model field for storing, retrieving, and converting measurement values.
    MeasurementField extends FloatField to handle values of MeasureBase or BidimensionalMeasure,
    allowing for unit-aware storage and conversion. It supports specifying the measurement class,
    default unit, and unit choices, and provides serialization/deserialization methods for
    database and string representations.

    Attributes:
        description (str): Description of the field's purpose.
        empty_strings_allowed (bool): Disallow empty strings as valid values.
        measurement (type): The measurement class (MeasureBase or BidimensionalMeasure).
        default_unit (str | None): The default unit for the measurement.
        unit_choices (list[str] | tuple[str] | None): Allowed unit choices.
        MEASURE_BASES (tuple): Tuple of valid measurement base classes.
        default_error_messages (dict): Error messages for invalid types.

    Args:
        verbose_name (str | None): Human-readable name for the field.
        name (str | None): Name of the field.
        measurement (type | None): The measurement class to use.
        measurement_class (str | None): Deprecated; name of the measurement class.
        default_unit (str | None): Default unit for the measurement.
        unit_choices (list[str] | tuple[str] | None): Allowed unit choices.
        args (list): Additional positional arguments.
        kwargs (dict): Additional keyword arguments.

    Raises:
        TypeError: If no measurement class is provided or if it is not a valid subclass.
    """
    description = "Easily store, retrieve, and convert python measures."
    empty_strings_allowed = False
    measurement: type[MeasureBase] | type[BidimensionalMeasure]
    default_unit: str | None
    unit_choices: list[str] | tuple[str] | None
    MEASURE_BASES = (
        BidimensionalMeasure,
        MeasureBase,
    )
    default_error_messages = {
        "invalid_type": _(
            "'%(value)s' (%(type_given)s) value" " must be of type %(type_wanted)s."
        ),
    }

    def __new__(cls, **kwargs):
        return super().__new__(cls)
    
    def __init__(
        self,
        verbose_name: str | None = None,
        name: str | None = None,
        measurement: type[MeasureBase] | type[BidimensionalMeasure] | None = None,
        measurement_class: str | None  = None,
        default_unit: str | None = None,
        unit_choices: list[str] | tuple[str] | None = None,
        *args,
        **kwargs
    ):

        if not measurement and measurement_class is not None:
            warnings.warn(
                '"measurement_class" will be removed in version 4.0', DeprecationWarning
            )
            measurement = getattr(measures, measurement_class)

        if not measurement:
            raise TypeError(
                "MeasurementField() takes a measurement"
                " keyword argument. None given."
            )

        if not issubclass(measurement, self.MEASURE_BASES):
            raise TypeError(
                "MeasurementField() takes a measurement keyword argument."
                " It has to be a valid MeasureBase subclass."
            )

        self.measurement = measurement
        self.default_unit = default_unit
        self.widget_args = {
            "measurement": measurement,
            "unit_choices": unit_choices,
            "default_unit": default_unit,
        }

        return super(MeasurementField, self).__init__(verbose_name, name, *args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(MeasurementField, self).deconstruct()
        kwargs["measurement"] = self.measurement
        kwargs["default_unit"] = self.default_unit
        return name, path, args, kwargs

    def get_prep_value(self, value):
        """
        Prepares the value for database storage.

        If the value is None, returns None.
        If the value is an instance of MEASURE_BASES, converts its 'standard' attribute to a float.
        Otherwise, delegates preparation to the superclass implementation.

        Args:
            value (Any): The value to prepare for storage.

        Returns:
            (Any): The prepared value suitable for database storage.
        """
        if value is None:
            return None

        elif isinstance(value, self.MEASURE_BASES):
            # sometimes we get sympy.core.numbers.Float, which the
            # database does not understand, so explicitely convert to
            # float

            return float(value.standard)

        else:
            return super(MeasurementField, self).get_prep_value(value)

    def get_default_unit(self):
        """
        Returns the default unit for the measurement field.

        The method checks for a default unit specified in `widget_args["default_unit"]`.
        If not found, it returns the first unit from `widget_args["unit_choices"]`.
        If neither is available, it falls back to the standard unit defined in `self.measurement.STANDARD_UNIT`.

        Returns:
            (str): The default unit for the measurement field.
        """
        default_unit = self.widget_args["default_unit"]
        if default_unit:
            return default_unit
        unit_choices = self.widget_args["unit_choices"]
        if unit_choices:
            return unit_choices[0][0]
        return self.measurement.STANDARD_UNIT

    def from_db_value(self, value, *args, **kwargs):
        """
        Converts a value retrieved from the database into a measurement object.

        Args:
            value (Any): The value retrieved from the database.
            args (list): Additional positional arguments (unused).
            kwargs (dict): Additional keyword arguments (unused).

        Returns:
            (Measure | None): A measurement object created using the specified measure, value, and the default unit, or None if the value is None.
        """
        if value is None:
            return None

        return get_measurement(
            measure=self.measurement,
            value=value,
            original_unit=self.get_default_unit(),
        )

    def value_to_string(self, obj):
        """
        Converts the value obtained from the given object to its string representation.

        If the value is not an instance of MEASURE_BASES, it returns the value as is.
        Otherwise, it returns a string in the format 'value:unit', where 'value' and 'unit'
        are attributes of the MEASURE_BASES instance.

        Args:
            obj (object): The object from which to extract the value.

        Returns:
            (str): The string representation of the value.
        """
        value = self.value_from_object(obj)
        if not isinstance(value, self.MEASURE_BASES):
            return value
        return "%s:%s" % (value.value, value.unit)

    def deserialize_value_from_string(self, s: str):
        """
        Deserializes a string representation of a measurement value and unit.

        The input string should be in the format "value:unit", where `value` is a float
        and `unit` is a string representing the measurement unit.

        Args:
            s (str): The string to deserialize, expected in the format "value:unit".

        Returns:
            (Measure | None): A Measurement object constructed from the value and unit, or None if the input string is not in the expected format.
        """
        parts = s.split(":", 1)
        if len(parts) != 2:
            return None
        value, unit = float(parts[0]), parts[1]
        measure = get_measurement(measure=self.measurement, value=value, unit=unit)
        return measure

    def to_python(self, value):
        """
        Converts the input value to a measurement object of the expected type.

        Handles various input types:
        - If `value` is None, returns None.
        - If `value` is already an instance of the expected measurement base type, returns it as-is.
        - If `value` is a string, attempts to deserialize it into a measurement object.
        - Otherwise, uses the superclass's `to_python` method to process the value.

        If the value is not already a measurement object, constructs one using the default unit,
        and logs a message indicating the type conversion and the guessed unit.

        Args:
            value (Any): The input value to be converted.

        Returns:
            (Measure | None): An instance of the expected measurement type, or None if input is None.
        """

        if value is None:
            return value
        elif isinstance(value, self.MEASURE_BASES):
            return value
        elif isinstance(value, str):
            parsed = self.deserialize_value_from_string(value)
            if parsed is not None:
                return parsed
        value = super(MeasurementField, self).to_python(value)

        return_unit = self.get_default_unit()

        msg = (
            'You assigned a %s instead of %s to %s.%s.%s, unit was guessed to be "%s".'
            % (
                type(value).__name__,
                str(self.measurement.__name__),
                self.model.__module__,
                self.model.__name__,
                self.name,
                return_unit,
            )
        )
        return get_measurement(
            measure=self.measurement,
            value=value,
            unit=return_unit,
        )
