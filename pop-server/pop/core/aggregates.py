from django.db.models import Aggregate, FloatField

class Median(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'median'
    output_field = FloatField()
    template = '%(function)s(0.5) WITHIN GROUP (ORDER BY %(expressions)s)'

class Percentile75(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'p75'
    output_field = FloatField()
    template = '%(function)s(0.75) WITHIN GROUP (ORDER BY %(expressions)s)'

class Percentile25(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'p25'
    output_field = FloatField()
    template = '%(function)s(0.25) WITHIN GROUP (ORDER BY %(expressions)s)'