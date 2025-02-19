from ninja import Schema
from typing import Tuple, Optional,  Union, Any
from enum import Enum 
from pop.oncology import schemas as oncology_schemas
from pop.core.schemas.factory import ModelGetSchema

DataResource = Enum('DataResource', {
    model.__name__.upper(): model.__name__ for model in oncology_schemas.ONCOLOGY_SCHEMAS if issubclass(model, ModelGetSchema)
}, type=str)

class DatasetRule(Schema):
    resource: DataResource # type: ignore
    field: str
    transform: Optional[Union[str, Tuple[str, Any]]] = None   
