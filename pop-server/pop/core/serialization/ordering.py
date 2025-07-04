from ninja_extra.ordering import Ordering as Orderingbase
from typing import Union, List, Optional
from django.db.models import QuerySet
from pop.core.utils import camel_to_snake


class Ordering(Orderingbase):

    def get_ordering(
        self, items: Union[QuerySet, List], value: Optional[str]
    ) -> List[str]:
        if value:
            fields = [param.strip() for param in value.split(",")]
            fields = [camel_to_snake(param) for param in fields]
            return fields
        return []
