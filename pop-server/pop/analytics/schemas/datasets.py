from datetime import date
from ninja import Schema, Field
from typing import List, Dict, Tuple, Optional,  Union
from enum import Enum 
from typing import ClassVar
from django.db.models import Subquery, OuterRef, F, Model
from django.db.models.functions import JSONObject
from django.contrib.postgres.aggregates import ArrayAgg
from pop.oncology import models as oncology_models
from pop.oncology import schemas as oncology_schemas
from pop.core.utils import get_related_model_from_field
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

DataResource = Enum('DataResource', {
    model.__name__.upper(): model.__name__ for model in oncology_schemas.ONCOLOGY_SCHEMAS if issubclass(model, ModelGetSchema)
}, type=str)

class DatasetDefinitionRule(Schema):
    resource: DataResource # type: ignore
    field: str
    transform: Optional[Union[str, Tuple[str, any]]] = None