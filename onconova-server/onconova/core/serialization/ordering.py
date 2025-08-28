from typing import List, Optional, Union

from django.db.models import QuerySet
from ninja_extra.ordering import Ordering as Orderingbase

from onconova.core.utils import camel_to_snake


class Ordering(Orderingbase):
    """
    Ordering class that extends Orderingbase to provide ordering functionality for querysets or lists.

    Methods
    -------
    get_ordering(items: Union[QuerySet, List], value: Optional[str]) -> List[str]
        Parses a comma-separated string of field names, strips whitespace, converts them from camelCase to snake_case,
        and returns them as a list of strings to be used for ordering. If no value is provided, returns an empty list.

    Parameters
    ----------
    items : Union[QuerySet, List]
        The collection of items to be ordered. Can be a Django QuerySet or a standard Python list.
    value : Optional[str]
        A comma-separated string of field names to order by.

    Returns
    -------
    List[str]
        A list of field names in snake_case to be used for ordering.
    """

    def get_ordering(
        self, items: Union[QuerySet, List], value: Optional[str]
    ) -> List[str]:
        """
        Generates a list of ordering fields from a comma-separated string.

        Args:
            items (Union[QuerySet, List]): The collection of items to be ordered. (Not used in this method, but may be required for interface compatibility.)
            value (Optional[str]): A comma-separated string specifying the ordering fields, possibly in camelCase.

        Returns:
            List[str]: A list of field names in snake_case to be used for ordering. Returns an empty list if no value is provided.
        """
        if value:
            fields = [param.strip() for param in value.split(",")]
            fields = [camel_to_snake(param) for param in fields]
            return fields
        return []
        return []
