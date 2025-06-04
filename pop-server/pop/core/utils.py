import re
import inspect
import hashlib
from uuid import UUID
from enum import Enum
from typing import Any, Union, get_args, get_origin, Optional, Literal

from pydantic import BaseModel, Field

from django.apps import apps
from django.db.models import Model as DjangoModel, QuerySet
from django.db.models.enums import ChoicesType
from django.core.exceptions import ObjectDoesNotExist

def is_optional(field: type) -> bool:
    """
    Check if a field is optional, i.e. its type is a Union containing None.

    Args:
        field (type): The field to check.

    Returns:
        bool: True if the field is optional, False otherwise.
    """
    return get_origin(field) is Union and \
           type(None) in get_args(field)

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
    return ''.join([
        word.lower() if n==0 else word.capitalize()
            for n,word in enumerate(string.split('_'))
    ])

def to_pascal_case(string: str) -> str:
    """
    Convert a string from snake_case to PascalCase.

    Args:
        string (str): The string to convert.

    Returns:
        str: The converted string.
    """
    if '_' in string:
        return ''.join([
            word.capitalize()
                for word in string.split('_')
        ])
    elif len(string)>1:
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

    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


    
def _get_deepest_args(tp: Any) -> list:
    """Recursively get the deepest type arguments of nested typing constructs."""
    args = get_args(tp)
    if not args:
        # Base case: no further nested types
        return [tp]
    # Recursively find the deepest types
    deepest_args = []
    for arg in args:
        deepest_args.extend(_get_deepest_args(arg))
    return deepest_args


def get_all_models_from_field(field: Field, issubclass_of: type = BaseModel) -> BaseModel:
    return (arg 
            for arg in _get_deepest_args(field.annotation) 
                if inspect.isclass(arg) and issubclass(arg, issubclass_of)
    )

def get_related_model_from_field(field: Field) -> Optional[BaseModel]:
    return next(get_all_models_from_field(field), None)

def find_uuid_across_models(search_uuid: Union[str,UUID], using: str = "default", app_label=None) -> Optional[DjangoModel]:
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
        if app_label and model._meta.app_label!=app_label:
            continue
        model_name = f"{model._meta.app_label}.{model.__name__}"
        try:
            match = model.objects.using(using).filter(pk=search_uuid).first()
            if match:
                return match
        except Exception as e:
            # Skip models with inaccessible fields or permissions
            continue

def revert_multitable_model(instance: DjangoModel, eventId: str) -> DjangoModel:
    # Get multi-table events 
    parent_event = instance.parent_events.filter(pgh_id=eventId).first()
    if parent_event:
        event = instance.events.filter(pgh_obj_id=parent_event.pgh_obj_id, pgh_created_at=parent_event.pgh_created_at).first()
    else:
        event = instance.events.filter(pgh_id=eventId).first()
        if event:
            parent_event = instance.parent_events.filter(pgh_obj_id=event.pgh_obj_id, pgh_created_at=event.pgh_created_at).first()
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


def hash_to_range(input_str: str, secret: str, low: int = -90, high: int = 90) -> int:
    # Combine input and secret
    combined = input_str + secret
    
    # Get SHA-256 hash as bytes
    hash_bytes = hashlib.sha256(combined.encode('utf-8')).digest()
    
    # Convert hash bytes to a large integer
    hash_int = int.from_bytes(hash_bytes, 'big')
    
    # Map to the range [low, high]
    range_size = high - low + 1
    mapped_value = low + (hash_int % range_size)
    
    return mapped_value