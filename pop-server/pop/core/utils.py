
from typing import Union, Literal, get_args, get_origin
from enum import Enum
from django.db.models.enums import ChoicesType

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

