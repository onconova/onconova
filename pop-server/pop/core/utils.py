
from typing import List, Any, Dict, Union, get_args, get_origin, Optional, Tuple, Literal
from enum import Enum
from pydantic import BaseModel, Field
import re
from django.db.models.enums import ChoicesType
import inspect

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

