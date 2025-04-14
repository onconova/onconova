from typing import Any, List, Tuple, Dict, Optional, Union

from datetime import datetime
from ninja.schema import ResolverMetaclass, Field
from pydantic.dataclasses import dataclass
from pydantic import AliasChoices 

from pop.core.models import BaseModel as OrmBaseModel

from .factory import create_schema
from .base import BaseSchema 

_is_modelschema_class_defined = False

CREATE_IGNORED_FIELDS = (
    'id', 
)  

@dataclass
class SchemaConfig:
    model: Any
    schema_name: Optional[str] = None
    fields: Optional[Union[List[str], Tuple[str]]] = None
    exclude: Optional[Union[List[str], Tuple[str]]] = None
    expand: Optional[Dict] = None

class ModelSchemaMetaclassBase(ResolverMetaclass):
    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs,):
        # Extract the metaclass configuration from the namespace
        metaclass_config = namespace.pop('config', None)
        # Construct base metaclass
        cls = super().__new__(mcs, name, bases, namespace, **kwargs,)
        for base in reversed(bases):
            if (_is_modelschema_class_defined and issubclass(base, (ModelGetSchema, ModelCreateSchema)) and base in (ModelGetSchema, ModelCreateSchema)):
                # Get the fields defined on the metaclass' namespace
                custom_fields = []
                annotations = namespace.get("__annotations__", {})
                for attr_name, type in annotations.items():
                    if attr_name.startswith("_"):
                        continue
                    default = namespace.get(attr_name, ...)
                    custom_fields.append((attr_name, type, default))
                    
                # If it is a get schema, add description field to the custom schema fields
                if issubclass(base, ModelGetSchema) and issubclass(metaclass_config.model, OrmBaseModel):
                    custom_fields.append(
                        ('description', str, Field(description='Human-readable description')),
                    )
                    if hasattr(metaclass_config.model, 'pgh_event_model'):
                        custom_fields.extend((
                            ('createdAt', datetime, Field(description='Date-time when the resource was created', alias='created_at', validation_alias=AliasChoices('createdAt','created_at'))),
                            ('updatedAt', Optional[datetime], Field(default=None, description='Date-time when the resource was last updated', alias='updated_at', validation_alias=AliasChoices('updatedAt','updated_at'))),
                            ('createdBy', Optional[str], Field(description='Username of the user who created the resource', alias='created_by', validation_alias=AliasChoices('createdBy','created_by'))),
                            ('updatedBy', Optional[List[str]], Field(default=None,description='Usernames of the users who have updated the resource', alias='updated_by', validation_alias=AliasChoices('updatedBy','updated_by'))),
                        ))
                
                # If it is a creation schema, add the ignored model fields to the exclude list
                exclude = list(metaclass_config.exclude or [])
                if issubclass(base, ModelCreateSchema) and issubclass(metaclass_config.model, OrmBaseModel):
                    exclude.extend(list(CREATE_IGNORED_FIELDS))
                    
                # If the new schema's name was not specified, base it on the model name by default 
                schema_name = metaclass_config.schema_name or (metaclass_config.model.__name__ + ('Create' if issubclass(base, ModelCreateSchema) else ''))

                # Construct the schema from the model dynamically
                model_schema = create_schema(
                    metaclass_config.model,
                    name=schema_name,
                    fields=metaclass_config.fields,
                    exclude=exclude,
                    expand=metaclass_config.expand,
                    custom_fields=custom_fields,
                    base_class=cls,
                )
                model_schema.__doc__ = cls.__doc__
                return model_schema
        return cls

class ModelGetSchema(BaseSchema, metaclass=ModelSchemaMetaclassBase):
    pass 

class ModelCreateSchema(BaseSchema, metaclass=ModelSchemaMetaclassBase):
    pass 

_is_modelschema_class_defined = True
