from ninja import Schema, Field
from typing import Tuple, Optional,  Union, Any, List
from enum import Enum 
from django.db.models import Q
from pop.oncology import schemas as oncology_schemas
from pop.analytics import models as orm
from pop.core.schemas.factory import create_filters_schema
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

DataResource = Enum('DataResource', {
    model.__name__.upper(): model.__name__ for model in oncology_schemas.ONCOLOGY_SCHEMAS if issubclass(model, ModelGetSchema)
}, type=str)

class DatasetRule(Schema):
    resource: DataResource # type: ignore
    relatedResource: Optional[DataResource] = None # type: ignore
    field: str
    transform: Optional[Union[str, Tuple[str, Any]]] = None   


class Dataset(ModelGetSchema):
    rules: List[DatasetRule] = Field([], description='Composition rules of the dataset')
    config = SchemaConfig(model=orm.Dataset)
    
class DatasetCreate(ModelCreateSchema):
    rules: List[DatasetRule] = Field([], description='Composition rules of the dataset')
    config = SchemaConfig(model=orm.Dataset)
    
DatasetFiltersBase = create_filters_schema(
    schema = Dataset, 
    name='DatasetFilters'
)

class DatasetFilters(DatasetFiltersBase):
    createdBy: Optional[str] = Field(None, description='Filter for a particular cohort creator by its username')

    def filter_createdBy(self, value: str) -> Q:
        return Q(created_by__username=self.createdBy) if value is not None else Q()
    