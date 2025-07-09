import re
import inspect
from datetime import datetime
import hashlib
import math
from uuid import UUID
from enum import Enum
from typing import Any, Union, get_args, get_origin, Optional, Literal

from pydantic import BaseModel, Field

from django.apps import apps
from django.db.models import Model as DjangoModel, QuerySet
from django.db.models.enums import ChoicesType
from django.core.exceptions import ObjectDoesNotExist

COMMON_HTTP_ERRORS = {404: None, 401: None, 403: None, 500: None}


def is_optional(field: type) -> bool:
    """
    Check if a field is optional, i.e. its type is a Union containing None.

    Args:
        field (type): The field to check.

    Returns:
        bool: True if the field is optional, False otherwise.
    """
    return get_origin(field) is Union and type(None) in get_args(field)


def is_union(field: type) -> bool:
    """
    Check if a field is optional, i.e. its type is a Union containing None.

    Args:
        field (type): The field to check.

    Returns:
        bool: True if the field is optional, False otherwise.
    """
    return get_origin(field) is Union


def is_list(field):
    """
    Check if a field is a list.

    Args:
        field (type): The field to check.

    Returns:
        bool: True if the field is a list, False otherwise.
    """
    return get_origin(field) is list


def is_enum(field: type) -> bool:
    """
    Check if a field is an enumeration.

    Args:
        field (type): The field to check.

    Returns:
        bool: True if the field is an enumeration, False otherwise.
    """
    return field.__class__ is type(Enum) or type(field) is ChoicesType


def is_literal(field: type) -> bool:
    """
    Check if a field is a literal value, i.e. its type is a Literal.

    Args:
        field (type): The field to check.

    Returns:
        bool: True if the field is a literal value, False otherwise.
    """
    return get_origin(field) is Literal


def to_camel_case(string: str) -> str:
    """
    Convert a string from snake_case to camelCase.

    Args:
        string (str): The string to convert.

    Returns:
        str: The converted string.
    """
    return "".join(
        [
            word.lower() if n == 0 else word.capitalize()
            for n, word in enumerate(string.split("_"))
        ]
    )


def to_pascal_case(string: str) -> str:
    """
    Convert a string from snake_case to PascalCase.

    Args:
        string (str): The string to convert.

    Returns:
        str: The converted string.
    """
    if "_" in string:
        return "".join([word.capitalize() for word in string.split("_")])
    elif len(string) > 1:
        return string[0].upper() + string[1:]
    else:
        return string.upper()


def camel_to_snake(name: str) -> str:
    """
    Convert a string from camelCase to snake_case.

    Args:
        name (str): The string to convert.

    Returns:
        str: The converted string in snake_case format.
    """

    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _get_deepest_args(tp: Any) -> list:
    """
    Recursively traverse nested type hints to find the deepest types.

    For example, if the input type is Union[List[Tuple[int, str]], float], the
    function will return [int, str, float].

    Args:
        tp (Any): The type to traverse.

    Returns:
        list: A list of the deepest types.
    """
    args = get_args(tp)
    if not args:
        # Base case: no further nested types
        return [tp]
    # Recursively find the deepest types
    deepest_args = []
    for arg in args:
        deepest_args.extend(_get_deepest_args(arg))
    return deepest_args


def get_all_models_from_field(
    field: Field, issubclass_of: type = BaseModel
) -> BaseModel:
    """
    Returns a generator of all models that are nested in a given field.

    Args:
        field (Field): The field to traverse.
        issubclass_of (type, optional): Filter results to only include classes
            that are subclasses of this type. Defaults to BaseModel.

    Yields:
        BaseModel: A model that is nested in the given field.
    """

    return (
        arg
        for arg in _get_deepest_args(field.annotation)
        if inspect.isclass(arg) and issubclass(arg, issubclass_of)
    )


def get_related_model_from_field(field: Field) -> Optional[BaseModel]:
    """
    Return the first model that is nested in a given field.

    Args:
        field (Field): The field to traverse.

    Returns:
        Optional[BaseModel]: The first model that is nested in the given field.
    """
    return next(get_all_models_from_field(field), None)


def find_uuid_across_models(
    search_uuid: Union[str, UUID], using: str = "default", app_label=None
) -> Optional[DjangoModel]:
    """
    Searches all models with UUIDFields for a specific UUID value.

    Args:
        search_uuid (Union[str,UUID]): The UUID string to search for.
        using (str): The database alias (defaults to "default").
        app_label (Optional[str]): The app's label on which to search for. If not specified, defaults to all apps.

    Returns:
        Django model instance if found, else None.
    """
    for model in apps.get_models():
        if app_label and model._meta.app_label != app_label:
            continue
        try:
            match = model.objects.using(using).filter(pk=search_uuid).first()
            if match:
                return match
        except Exception as e:
            # Skip models with inaccessible fields or permissions
            continue


def revert_multitable_model(instance: DjangoModel, eventId: str) -> DjangoModel:
    """
    Revert a multi-table Django model to a specific history event.

    This function is specifically designed to work with multi-table Django models
    that are versioned using pghistory. It will find the history event with the given
    ID and revert the instance to that point in time.

    :param instance: The instance to revert.
    :param eventId: The ID of the history event to revert to.
    :return: The reverted instance.
    :raises ObjectDoesNotExist: If no matching history event exists.
    """
    # Get multi-table events
    parent_event = instance.parent_events.filter(pgh_id=eventId).first()
    if parent_event:
        event = instance.events.filter(
            pgh_obj_id=parent_event.pgh_obj_id,
            pgh_created_at=parent_event.pgh_created_at,
        ).first()
    else:
        event = instance.events.filter(pgh_id=eventId).first()
        if event:
            parent_event = instance.parent_events.filter(
                pgh_obj_id=event.pgh_obj_id, pgh_created_at=event.pgh_created_at
            ).first()
    if not event and not parent_event:
        raise ObjectDoesNotExist()

    # Revert the events for all tables
    if parent_event:
        # Parent event is always model-complete and can be handled by pghistory
        instance = parent_event.revert()
    if event:
        # Child event is not model-complete according to pghistory and must be reverted manually
        qset = QuerySet(model=event.pgh_tracked_model)
        pk = getattr(event, event.pgh_tracked_model._meta.pk.name)
        instance = qset.update_or_create(
            pk=pk,
            defaults={
                field.name: getattr(event, field.name)
                for field in event.pgh_tracked_model._meta.fields
                if field != event.pgh_tracked_model._meta.pk
                and hasattr(event, field.name)
            },
        )[0]
    return instance


def is_datetime(date_string: str, date_format: str) -> bool:
    """
    Checks if a given string can be parsed as a datetime object with the given date format.

    Args:
        date_string: The string to be parsed.
        date_format: The date format to use for parsing.

    Returns:
        True if the string can be parsed as a datetime object with the given date format,
        False otherwise.
    """
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False


def is_period(period_string, date_format):
    """
    Checks if a given string can be parsed as a period string with the given date format.

    Args:
        period_string: The string to be parsed.
        date_format: The date format to use for parsing.

    Returns:
        True if the string can be parsed as a period string with the given date format,
        False otherwise.
    """
    try:
        period_start_string, period_end_string = period_string.strip("()[]").split(",")
        datetime.strptime(period_start_string, date_format)
        datetime.strptime(period_end_string, date_format)
        return True
    except ValueError:
        return False


def hash_to_range(input_str: str, secret: str, low: int = -90, high: int = 90) -> int:
    """
    Maps a given string to a random integer in the range [low, high] deterministically
    using the given secret string.

    The function works by combining the input string with the secret string and then
    computing the SHA-256 hash of the combined string. The hash is then converted to a
    large integer and mapped to the range [low, high] using the modulo operator.

    Args:
        input_str: The string to be mapped.
        secret: The secret string used for hashing.
        low: The lowest value of the range (default: -90).
        high: The highest value of the range (default: 90).

    Returns:
        An integer in the range [low, high] that is deterministically mapped from the
        input string.
    """
    combined = input_str + secret

    # Get SHA-256 hash as bytes
    hash_bytes = hashlib.sha256(combined.encode("utf-8")).digest()

    # Convert hash bytes to a large integer
    hash_int = int.from_bytes(hash_bytes, "big")

    # Map to the range [low, high]
    range_size = high - low + 1
    mapped_value = low + (hash_int % range_size)

    return mapped_value


def percentile(data, q):
    """
    Pure Python percentile function
    Supports single q value (0-100)
    """
    if not data:
        raise ValueError("Cannot compute percentile of empty data")

    if not (0 <= q <= 100):
        raise ValueError("Percentile must be between 0 and 100")

    sorted_data = sorted(data)
    n = len(sorted_data)
    rank = (q / 100) * (n - 1)
    lower_idx = int(math.floor(rank))
    upper_idx = int(math.ceil(rank))

    if lower_idx == upper_idx:
        return sorted_data[int(rank)]

    lower_value = sorted_data[lower_idx]
    upper_value = sorted_data[upper_idx]
    weight = rank - lower_idx

    return lower_value + weight * (upper_value - lower_value)


def average(data, weights=None):
    """
    Pure Python average function
    """
    if not data:
        raise ValueError("Cannot compute average of empty data")

    if weights is None:
        return sum(data) / len(data)

    if len(weights) != len(data):
        raise ValueError("Data and weights must be the same length")

    weighted_sum = sum(d * w for d, w in zip(data, weights))
    total_weight = sum(weights)

    if total_weight == 0:
        raise ValueError("Sum of weights cannot be zero")

    return weighted_sum / total_weight


def median(data):
    """
    Pure Python median function
    """
    if not data:
        raise ValueError("Cannot compute median of empty data")

    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2

    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        return sorted_data[mid]


def std(data, ddof=0):
    """
    Pure Python standard deviation function

    Args:
        data (list): List of numeric values
        ddof (int): Delta Degrees of Freedom (0 for population, 1 for sample)

    Returns:
        float: Standard deviation of the data
    """
    n = len(data)
    if n == 0:
        raise ValueError("Cannot compute standard deviation of empty data")
    if n - ddof <= 0:
        raise ValueError("Degrees of freedom <= 0. Increase data size or reduce ddof.")

    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / (n - ddof)
    return math.sqrt(variance)
