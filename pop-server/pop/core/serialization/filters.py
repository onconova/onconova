from datetime import date
from functools import partial
from typing import Any, Callable, List, Optional, Tuple, Type, Union

from django.db.models import Count
from django.db.models import Model as DjangoModel
from django.db.models import Q, QuerySet
from django.db.models.expressions import RawSQL
from ninja import FilterSchema, Schema
from pydantic import BaseModel
from pydantic.fields import FieldInfo


class FilterBaseSchema(FilterSchema):
    """
    Base schema for Django ORM-compatible filtering.

    Provides:
    - Automatic mapping of filters to queryset expressions.
    - Field-specific filter resolution via method naming conventions.
    """

    _queryset_model: Type[DjangoModel] | None = None

    def filter(self, queryset: QuerySet) -> QuerySet:
        """
        Apply all schema-defined filters to a queryset.

        Args:
            queryset (QuerySet): The Django queryset to filter.

        Returns:
            QuerySet: The filtered queryset.
        """
        self._queryset_model = queryset.model
        filtered_queryset = queryset.filter(self.get_filter_expression())
        self._queryset_model = None
        return filtered_queryset

    def get_filter(self, field_name: str) -> Callable:
        """
        Retrieve a custom filter method by its field name.

        Args:
            field_name (str): The schema field to resolve a filter for.

        Returns:
            Callable: The custom filter function.
        """
        method_name = f"filter_{field_name}".replace(".", "_")
        return getattr(self, method_name)

    def _resolve_field_expression(
        self, field_name: str, field_value: Any, field: FieldInfo
    ) -> Q:
        """
        Convert a schema field and value into a Django Q expression.

        Args:
            field_name (str): The schema field name.
            field_value (Any): The value being filtered on.
            field (FieldInfo): The field's metadata.

        Returns:
            Q: A Django Q expression representing the filter.
        """
        field_name = field_name.replace(".", "_")
        return super()._resolve_field_expression(field_name, field_value, field)


class DjangoFilter:
    """
    Base class for defining custom Django-compatible ORM filters.

    Attributes:
        name (str): Human-readable filter label.
        lookup (str): Django ORM lookup string (e.g. 'icontains', 'gte').
        description (str): Description for documentation and OpenAPI.
        value_type (type): The Python type of the expected filter value.
        negative (bool): Whether this filter negates its result.
    """

    name: str = ""
    lookup: str = ""
    description: str = ""
    value_type: type
    negative: bool = False

    @staticmethod
    def query_expression(
        schema: Any, value: Any, field: str, lookup: str, negative: bool
    ) -> Q:
        """
        Build a Django Q query expression for a given filter configuration.

        Args:
            schema (Any): Schema context (unused here, but allows future customization).
            value (Any): The value to filter against.
            field (str): The field name on the model.
            lookup (str): The Django lookup to apply.
            negative (bool): Whether to invert the query expression.

        Returns:
            Q: The constructed Django Q query.
        """
        if value is None:
            return Q()

        query = Q(**{f"{field}__{lookup}": value})
        return ~query if negative else query

    @classmethod
    def generate_query_expression(cls, field: str) -> Callable:
        """
        Create a partial function to evaluate a query expression for this filter.

        Args:
            field (str): The model field name.

        Returns:
            Callable: A partial query expression function.
        """
        return partial(
            cls.query_expression, field=field, lookup=cls.lookup, negative=cls.negative
        )

    @classmethod
    def get_query(
        cls,
        field: str,
        value: Any,
        model: Optional[Union[BaseModel, DjangoModel]] = None,
    ) -> Q:
        """
        Build a query expression for a given value and field.

        Args:
            field (str): The model field name.
            value (Any): The value to filter on.
            model (Optional[Union[BaseModel, DjangoModel]]): Optionally, the model instance or schema context.

        Returns:
            Q: The resulting Django Q query.
        """
        return cls.query_expression(
            model, value=value, field=field, lookup=cls.lookup, negative=cls.negative
        )


class ExactStringFilter(DjangoFilter):
    name = ""
    description = "Filter for full text matches"
    value_type = str
    lookup = "iexact"


class NotExactStringFilter(ExactStringFilter):
    name = "not"
    description = "Filter for full text mismatches"
    value_type = str
    negative = True


class ContainsStringFilter(DjangoFilter):
    name = "contains"
    description = "Filter for partial text matches"
    value_type = str
    lookup = "icontains"


class NotContainsStringFilter(ContainsStringFilter):
    name = "not.contains"
    description = "Filter for partial text mismatches"
    negative = True


class BeginsWithStringFilter(DjangoFilter):
    name = "beginsWith"
    description = "Filter for entries starting with the text"
    value_type = str
    lookup = "istartswith"


class NotBeginsWithStringFilter(BeginsWithStringFilter):
    name = "not.beginsWith"
    description = "Filter for entries not starting with the text"
    negative = True


class EndsWithStringFilter(DjangoFilter):
    name = "endsWith"
    description = "Filter for entries ending with the text"
    value_type = str
    lookup = "iendswith"


class NotEndsWithStringFilter(EndsWithStringFilter):
    name = "not.endsWith"
    description = "Filter for entries not ending with the text"
    negative = True


class AnyOfStringFilter(DjangoFilter):
    name = "anyOf"
    description = "Filter for entries where at least one reference matches the query"
    value_type = List[str]
    lookup = "in"


class NotAnyOfStringFilter(AnyOfStringFilter):
    name = "not.anyOf"
    description = "Filter for entries where at least one reference mismatches the query"
    negative = True


STRING_FILTERS = (
    ExactStringFilter,
    NotExactStringFilter,
    ContainsStringFilter,
    NotContainsStringFilter,
    BeginsWithStringFilter,
    NotBeginsWithStringFilter,
    EndsWithStringFilter,
    NotEndsWithStringFilter,
    AnyOfStringFilter,
    NotAnyOfStringFilter,
)


class IsNullFilter(DjangoFilter):
    name = "not.exists"
    description = "Filter for entries without a value"
    value_type = bool
    lookup = "isnull"


class NotIsNullFilter(IsNullFilter):
    name = "exists"
    description = "Filter for entries with a value"
    negative = True


NULL_FILTERS = (IsNullFilter, NotIsNullFilter)


class BeforeDateFilter(DjangoFilter):
    name = "before"
    lookup = "lt"
    description = "Filter for entries with dates before the specified value"
    value_type = date


class AfterDateFilter(DjangoFilter):
    name = "after"
    lookup = "gt"
    description = "Filter for entries with dates after the specified value"
    value_type = date


class OnOrBeforeDateFilter(DjangoFilter):
    name = "onOrBefore"
    lookup = "lte"
    description = "Filter for entries with dates on or before the specified value"
    value_type = date


class OnOrAfterDateFilter(DjangoFilter):
    name = "onOrAfter"
    lookup = "gte"
    description = "Filter for entries with dates on or after the specified value"
    value_type = date


class OnDateFilter(DjangoFilter):
    name = "on"
    lookup = "exact"
    description = "Filter for entries with dates exactly matching the specified value"
    value_type = date


class NotOnDateFilter(OnDateFilter):
    name = "not.on"
    description = "Filter for entries with dates not matching the specified value"
    negative = True


class BetweenDatesFilter(DjangoFilter):
    name = "between"
    lookup = "range"
    description = (
        "Filter for entries with dates between two specified values (inclusive)"
    )
    value_type = Tuple[date, date]


class NotBetweenDatesFilter(BetweenDatesFilter):
    name = "not.between"
    description = (
        "Filter for entries with dates not between two specified values (inclusive)"
    )
    negative = True


DATE_FILTERS = (
    BeforeDateFilter,
    AfterDateFilter,
    OnOrBeforeDateFilter,
    OnOrAfterDateFilter,
    OnDateFilter,
    NotOnDateFilter,
    BetweenDatesFilter,
    NotBetweenDatesFilter,
)


class LessThanIntegerFilter(DjangoFilter):
    name = "lessThan"
    lookup = "lt"
    description = "Filter for entries with values less than the specified value"
    value_type = int


class LessThanOrEqualIntegerFilter(DjangoFilter):
    name = "lessThanOrEqual"
    lookup = "lte"
    description = (
        "Filter for entries with values less than or equal to the specified value"
    )
    value_type = int


class GreaterThanIntegerFilter(DjangoFilter):
    name = "greaterThan"
    lookup = "gt"
    description = "Filter for entries with values greater than the specified value"
    value_type = int


class GreaterThanOrEqualIntegerFilter(DjangoFilter):
    name = "greaterThanOrEqual"
    lookup = "gte"
    description = (
        "Filter for entries with values greater than or equal to the specified value"
    )
    value_type = int


class EqualIntegerFilter(DjangoFilter):
    name = "equal"
    lookup = "exact"
    description = "Filter for entries with values exactly equal to the specified value"
    value_type = int


class NotEqualIntegerFilter(EqualIntegerFilter):
    name = "not.equal"
    description = "Filter for entries with values not equal to the specified value"
    negative = True


class BetweenIntegerFilter(DjangoFilter):
    name = "between"
    lookup = "range"
    description = (
        "Filter for entries with values between two specified values (inclusive)"
    )
    value_type = Tuple[int, int]


class NotBetweenIntegerFilter(BetweenIntegerFilter):
    name = "not.between"
    description = (
        "Filter for entries with values between two specified values (inclusive)"
    )
    negative = True


INTEGER_FILTERS = (
    LessThanIntegerFilter,
    LessThanOrEqualIntegerFilter,
    GreaterThanIntegerFilter,
    GreaterThanOrEqualIntegerFilter,
    EqualIntegerFilter,
    NotEqualIntegerFilter,
    BetweenIntegerFilter,
    NotBetweenIntegerFilter,
)


class LessThanFloatFilter(DjangoFilter):
    name = "lessThan"
    lookup = "lt"
    description = "Filter for entries with values less than the specified value"
    value_type = float


class LessThanOrEqualFloatFilter(DjangoFilter):
    name = "lessThanOrEqual"
    lookup = "lte"
    description = (
        "Filter for entries with values less than or equal to the specified value"
    )
    value_type = float


class GreaterThanFloatFilter(DjangoFilter):
    name = "greaterThan"
    lookup = "gt"
    description = "Filter for entries with values greater than the specified value"
    value_type = float


class GreaterThanOrEqualFloatFilter(DjangoFilter):
    name = "greaterThanOrEqual"
    lookup = "gte"
    description = (
        "Filter for entries with values greater than or equal to the specified value"
    )
    value_type = float


class EqualFloatFilter(DjangoFilter):
    name = "equal"
    lookup = "exact"
    description = "Filter for entries with values exactly equal to the specified value"
    value_type = float


class NotEqualFloatFilter(EqualFloatFilter):
    name = "not.equal"
    description = "Filter for entries with values not equal to the specified value"
    negative = True


class BetweenFloatFilter(DjangoFilter):
    name = "between"
    lookup = "range"
    description = (
        "Filter for entries with values between two specified values (inclusive)"
    )
    value_type = Tuple[float, float]


class NotBetweenFloatFilter(BetweenFloatFilter):
    name = "not.between"
    description = (
        "Filter for entries with values between two specified values (inclusive)"
    )
    negative = True


FLOAT_FILTERS = (
    LessThanFloatFilter,
    LessThanOrEqualFloatFilter,
    GreaterThanFloatFilter,
    GreaterThanOrEqualFloatFilter,
    EqualFloatFilter,
    NotEqualFloatFilter,
    BetweenFloatFilter,
    NotBetweenFloatFilter,
)


class EqualsBooleanFilter(DjangoFilter):
    name = ""
    lookup = "exact"
    description = "Filter for yes/no statement"
    value_type = bool


BOOLEAN_FILTERS = (EqualsBooleanFilter,)


class EqualsEnumFilter(DjangoFilter):
    name = ""
    lookup = "exact"
    description = "Filter for single value choice"
    value_type = str


class NotEqualsEnumFilter(EqualsEnumFilter):
    name = "not"
    description = ("Filter for all but a single value choice",)
    negative = True


class AnyOfEnumFilter(DjangoFilter):
    name = "anyOf"
    lookup = "in"
    description = "Filter for subset of value choices"
    value_type = List[str]


class NotAnyOfEnumFilter(AnyOfEnumFilter):
    name = "anyOf"
    description = ("Filter for excluding a subset of value choices",)
    negative = True


ENUM_FILTERS = (
    EqualsEnumFilter,
    NotEqualsEnumFilter,
    AnyOfEnumFilter,
    NotAnyOfEnumFilter,
)


class EqualsReferenceFilter(DjangoFilter):
    name = ""
    lookup = "exact"
    description = "Filter for a matching reference Id"
    value_type = str


class NotEqualsReferenceFilter(EqualsReferenceFilter):
    name = "not.equals"
    description = "Filter for a mismatching reference Id"
    negative = True


class OneOfReferenceFilter(DjangoFilter):
    name = "oneOf"
    lookup = "in"
    description = "Filter for a subset of matching reference Ids"
    value_type = List[str]


class NotOneOfReferenceFilter(OneOfReferenceFilter):
    name = "not.oneOf"
    description = "Filter for a subset of mismatching reference Ids"
    negative = True


REFERENCE_FILTERS = (
    EqualsReferenceFilter,
    NotEqualsReferenceFilter,
    OneOfReferenceFilter,
    NotOneOfReferenceFilter,
)


class EqualsConceptFilter(DjangoFilter):
    name = ""
    lookup = "code__iexact"
    description = "Filter for a matching concept code"
    value_type = str


class NotEqualsConceptFilter(EqualsConceptFilter):
    name = "not"
    description = "Filter for a mismatching concept code"
    negative = True


class AnyOfConceptFilter(DjangoFilter):
    name = "anyOf"
    lookup = "code__in"
    description = "Filter for a matching set of concept codes"
    value_type = List[str]


class NotAnyOfConceptFilter(AnyOfConceptFilter):
    name = "not.anyOf"
    description = "Filter for a mismmatching set of concept codes"
    negative = True


class DescendantsOfConceptFilter(DjangoFilter):
    name = "descendantsOf"
    description = "Filter for all child concepts of a given concepts code"
    value_type = str

    @staticmethod
    def query_expression(model, value, field, lookup, negative):
        if value is None:
            return Q()
        if not model:
            raise ValueError(
                "The descendantsOf filter requires a model to be specified"
            )
        elif hasattr(model, "_queryset_model"):
            model = model._queryset_model
        terminology = model._meta.get_field(field).related_model
        concept = terminology.objects.get(code=value)
        # Get the correct database table name
        db_table = terminology._meta.db_table
        query = Q(
            **{
                f"{field}__in": terminology.objects.filter(
                    id__in=RawSQL(
                        f"""
            WITH RECURSIVE descendants AS (
                SELECT id FROM {db_table} WHERE id = %s
                UNION ALL
                SELECT cc.id FROM {db_table} cc
                JOIN descendants d ON cc.parent_id = d.id
            )
            SELECT id FROM descendants WHERE id != %s
        """,
                        [concept.id, concept.id],
                    )
                )
            }
        )
        return ~query if negative else query


CODED_CONCEPT_FILTERS = (
    EqualsConceptFilter,
    NotEqualsConceptFilter,
    AnyOfConceptFilter,
    NotAnyOfConceptFilter,
    DescendantsOfConceptFilter,
)


class AllOfConceptFilter(DjangoFilter):
    name = "allOf"
    description = "Filter for entries matching all of the concepts"
    value_type = List[str]

    @staticmethod
    def query_expression(model, value, field, lookup, negative):
        if value is None:
            return Q()
        if not model:
            raise ValueError("The allOf filter requires a model to be specified")
        elif hasattr(model, "_queryset_model"):
            model = model._queryset_model
        # Annotate the queryset with the count of related objects in the Many-to-Many field
        subquery = model.objects.annotate(m2m_entries_count=Count(field)).filter(
            m2m_entries_count=len(value)
        )
        # Filter the queryset further to include instances related to each value in the values list
        for entry in value:
            subquery = subquery.filter(**{f"{field}__code": entry})
        # Get the correct database table name
        query = Q(pk__in=subquery.values_list("pk", flat=True))
        return ~query if negative else query


class NotAllOfConceptFilter(AllOfConceptFilter):
    name = "not.allOf"
    description = "Filter for entries mismatching all of the concepts"
    negative = True


MULTI_CODED_CONCEPT_FILTERS = (
    *CODED_CONCEPT_FILTERS,
    AllOfConceptFilter,
    NotAllOfConceptFilter,
)


class OverlapsPeriodFilter(DjangoFilter):
    name = "overlaps"
    lookup = "overlap"
    description = "Filter for entries overlapping with the time period"
    value_type = Tuple[date, date]


class NotOverlapsPeriodFilter(OverlapsPeriodFilter):
    name = "not.overlaps"
    description = "Filter for entries not overlapping with the time period"
    negative = True


class ContainsPeriodFilter(DjangoFilter):
    name = "contains"
    lookup = "contains"
    description = "Filter for entries containing the time period"
    value_type = Tuple[date, date]


class NotContainsPeriodFilter(ContainsPeriodFilter):
    name = "not.contains"
    description = "Filter for entries not containing the time period"
    negative = True


class ContainedByPeriodFilter(DjangoFilter):
    name = "containedBy"
    lookup = "contained_by"
    description = "Filter for entries whose period are contined by the time period"
    value_type = Tuple[date, date]


class NotContainedByPeriodFilter(ContainedByPeriodFilter):
    name = "not.containedBy"
    description = "Filter for entries whose period are not contined by the time period"
    negative = True


PERIOD_FILTERS = (
    OverlapsPeriodFilter,
    NotOverlapsPeriodFilter,
    ContainsPeriodFilter,
    NotContainsPeriodFilter,
    ContainedByPeriodFilter,
    NotContainedByPeriodFilter,
)


class ExactRefereceFilter(DjangoFilter):
    name = ""
    description = "Filter for reference matches"
    value_type = str
    lookup = "exact"


class NotExactRefereceFilter(ExactStringFilter):
    name = "not"
    description = "Filter for reference mismatches"
    value_type = str
    negative = True


REFERENCE_FILTERS = (
    ExactRefereceFilter,
    NotExactRefereceFilter,
)


class AnyOfReferecesFilter(ExactRefereceFilter):
    name = "anyOf"
    description = "Filter for entries where at least one reference matches the query"


class NotAnyOfReferecesFilter(NotExactRefereceFilter):
    name = "not.anyOf"
    description = "Filter for entries where at least one reference mismatches the query"


class AllOfReferencesFilter(DjangoFilter):
    name = "allOf"
    description = "Filter for entries where all references match the query references"
    value_type = List[str]

    @staticmethod
    def query_expression(model, value, field, lookup, negative):
        if value is None:
            return Q()
        if not model:
            raise ValueError("The allOf filter requires a model to be specified")
        elif hasattr(model, "_queryset_model"):
            model = model._queryset_model
        # Annotate the queryset with the count of related objects in the Many-to-Many field
        subquery = model.objects.annotate(m2m_entries_count=Count(field)).filter(
            m2m_entries_count=len(value)
        )
        # Filter the queryset further to include instances related to each value in the values list
        for entry in value:
            subquery = subquery.filter(**{f"{field}": entry})
        # Get the correct database table name
        query = Q(pk__in=subquery.values_list("pk", flat=True))
        return ~query if negative else query


class NotAllOfReferencesFilter(AllOfConceptFilter):
    name = "not.allOf"
    description = (
        "Filter for entries where all references mismatch the query references"
    )
    negative = True


MULTI_REFERENCE_FILTERS = (
    AnyOfReferecesFilter,
    NotAnyOfReferecesFilter,
    AllOfReferencesFilter,
    NotAllOfReferencesFilter,
)


class ExactArrayFilter(DjangoFilter):
    name = ""
    description = "Filter for exact array matches"
    value_type = List[str]
    lookup = ""


class NotExactArrayFilter(ExactArrayFilter):
    name = "not"
    description = "Filter for exact array mismatches"
    value_type = List[str]
    negative = True


class ContainsArrayFilter(DjangoFilter):
    name = "contains"
    description = (
        "Filter for entries where where the values passed are a subset of the data"
    )
    value_type = List[str]
    lookup = "contains"


class NotContainsArrayFilter(ContainsArrayFilter):
    name = "not.contains"
    description = (
        "Filter for entries where the values passed are not a subset of the data"
    )
    value_type = List[str]
    negative = True


class ContainedByArrayFilter(DjangoFilter):
    name = "containedBy"
    description = (
        "Filter for entries where where the data is a subset of the values passed"
    )
    value_type = List[str]
    lookup = "contained_by"


class NotContainedByArrayFilter(ContainedByArrayFilter):
    name = "not.containedBy"
    description = (
        "Filter for entries where the data is not a subset of the values passed"
    )
    value_type = List[str]
    negative = True


class OverlapsArrayFilter(DjangoFilter):
    name = "overlaps"
    description = (
        "Filter for entries  where the data shares any results with the values passed."
    )
    value_type = List[str]
    lookup = "overlap"


class NotOverlapsByArrayFilter(OverlapsArrayFilter):
    name = "not.overlaps"
    description = "Filter for entries  where the data shares not any results with the values passed."
    value_type = List[str]
    negative = True


ARRAY_FILTERS = (
    ExactArrayFilter,
    NotExactArrayFilter,
    ContainsArrayFilter,
    NotContainsArrayFilter,
    ContainedByArrayFilter,
    NotContainedByArrayFilter,
    OverlapsArrayFilter,
    NotOverlapsByArrayFilter,
)


class ExactUserReferenceFilter(DjangoFilter):
    name = "username"
    description = "Filter for username matches"
    value_type = str
    lookup = "username__iexact"


class NotExactUserRefereceFilter(ExactStringFilter):
    name = "username.not"
    description = "Filter for username mismatches"
    value_type = str
    negative = True


class AnyOfUserRefereceFilter(ExactStringFilter):
    name = "username.anyOf"
    description = "Filter for entries where at least one reference mismatches the query"
    value_type = List[str]
    lookup = "username__in"


class NotAnyOfUserRefereceFilter(AnyOfUserRefereceFilter):
    name = "username.not.anyOf"
    description = "Filter for entries where at least one reference matches the query"
    value_type = str
    negative = True


USER_REFERENCE_FILTERS = (
    ExactUserReferenceFilter,
    NotExactUserRefereceFilter,
    AnyOfUserRefereceFilter,
    NotAnyOfUserRefereceFilter,
)


ALL_FILTERS = (
    *STRING_FILTERS,
    *DATE_FILTERS,
    *PERIOD_FILTERS,
    *INTEGER_FILTERS,
    *FLOAT_FILTERS,
    *BOOLEAN_FILTERS,
    *CODED_CONCEPT_FILTERS,
    *MULTI_CODED_CONCEPT_FILTERS,
    *REFERENCE_FILTERS,
    *MULTI_REFERENCE_FILTERS,
    *USER_REFERENCE_FILTERS,
    *ENUM_FILTERS,
    *NULL_FILTERS,
    *ARRAY_FILTERS,
)
