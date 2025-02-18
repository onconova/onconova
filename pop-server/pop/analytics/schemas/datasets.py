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
from pop.terminology.fields import CodedConceptField
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pydantic import BaseModel, Field, PrivateAttr, create_model

DataResource = Enum('DataResource', {
    model.__name__.upper(): model.__name__ for model in oncology_schemas.ONCOLOGY_SCHEMAS if issubclass(model, ModelGetSchema)
}, type=str)

class DatasetRule(Schema):
    resource: DataResource # type: ignore
    field: str
    transform: Optional[Union[str, Tuple[str, any]]] = None   
    _parent: "DatasetRule" = PrivateAttr(default=None)
    
    @property
    def resource_schema(self):
        return getattr(oncology_schemas, f'{self.resource.value}Schema')
    
    @property
    def resource_orm_model(self):
        return self.resource_schema.__orm_model__
    
    @property 
    def resource_orm_related_name(self):
        if self.resource_orm_model is oncology_models.PatientCase:
            return ''
        if self._parent:
            return {field.related_model: field.name for field in self._parent.resource_orm_model._meta.get_fields()}[self.resource_orm_model]
        return self.resource_orm_model._meta.get_field('case')._related_name

    @property 
    def schema_field(self):
        return self.resource_schema.model_fields.get(self.field)
    
    @property 
    def orm_field(self):
        return self.resource_orm_model._meta.get_field(self.schema_field.alias)

    @property 
    def child_resources(self):
        return [
            get_related_model_from_field(field).__name__ for field in self.resource_schema.model_fields.values() if get_related_model_from_field(field) and issubclass(get_related_model_from_field(field), ModelGetSchema) 
        ]
        
    @property
    def related_orm_lookup(self):
        print(self.orm_field)
        if isinstance(self.orm_field, CodedConceptField):
            return f'{self.resource_orm_related_name}__{self.orm_field.name}__display'
        else:
            return f'{self.resource_orm_related_name}__{self.orm_field.name}'

    @property 
    def annotation(self):
        return F(self.related_orm_lookup)

    @property 
    def annotation(self):
        return F(self.related_orm_lookup)
