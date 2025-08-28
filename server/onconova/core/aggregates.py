from django.db.models import Aggregate, FloatField


class Median(Aggregate):
    """
    Aggregate class that computes the median value of a given expression using the SQL
    PERCENTILE_CONT function. The median is calculated as the 0.5 percentile within the
    ordered group of the provided expressions. The result is returned as a floating-point value.
    """

    function = "PERCENTILE_CONT"
    name = "median"
    template = "%(function)s(0.5) WITHIN GROUP (ORDER BY %(expressions)s)"

    def get_output_field(self):
        return FloatField()


class Percentile75(Aggregate):
    """
    Aggregate class to compute the 75th percentile (p75) of a set of values.

    This class uses the SQL function `PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY ...)`
    to calculate the continuous 75th percentile, which is commonly used to measure
    the value below which 75% of the data falls.
    """

    function = "PERCENTILE_CONT"
    name = "p75"
    template = "%(function)s(0.75) WITHIN GROUP (ORDER BY %(expressions)s)"

    def get_output_field(self):
        return FloatField()


class Percentile25(Aggregate):
    """
    Aggregate that calculates the 25th percentile (first quartile) of a given expression using the SQL PERCENTILE_CONT function.
    """

    function = "PERCENTILE_CONT"
    name = "p25"
    template = "%(function)s(0.25) WITHIN GROUP (ORDER BY %(expressions)s)"

    def get_output_field(self):
        return FloatField()
