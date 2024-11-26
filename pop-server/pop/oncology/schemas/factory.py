from typing import Any,List, Tuple, Type, Optional

from django.db.models import Model as DjangoModel

from pydantic import create_model as create_pydantic_model, BaseModel as PydanticBaseModel, ConfigDict

from ninja.errors import ConfigError
from ninja.orm.factory import SchemaFactory as NinjaSchemaFactory
from ninja.schema import ResolverMetaclass, Schema

from pop.oncology.schemas.fields import get_schema_field, CodedConceptSchema

__all__ = ["SchemaFactory", "factory", "create_schema"]
_is_modelschema_class_defined = False

class BaseSchema(PydanticBaseModel):
    """
    Expands the Pydantic [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) to use aliases by default.    
    """    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name = True,
    )

    def model_dump(self, *args, **kwargs):
        """
        Override the Pydantic `model_dump` method to always use aliases and exclude None values.
        """
        kwargs.update({'by_alias': True, 'exclude_none': True})
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs):
        """
        Dumps the model as a JSON string.

        This method overrides the default behavior to ensure that aliases are 
        used and None values are excluded by default.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            str: The JSON string representation of the model.
        """
        # Update kwargs to use aliases and exclude None values
        kwargs.update({'by_alias': True, 'exclude_none': True})
        # Call the superclass method with updated arguments
        return super().model_dump_json(*args, **kwargs)

    def model_dump_django(
            self, 
            model: Type[DjangoModel] = None, 
            instance: Optional[DjangoModel] = None, 
            save: bool=False,
            user: Optional[DjangoModel]=None,
    ) -> DjangoModel:
        """
        Creates a Django model instance from the current schema.
        """
        model = model or self.__ormmodel__
        create = instance is None 
        if create:
            instance = model()
        for field in self.model_fields.keys():
            data = getattr(self, field)
            if isinstance(data, CodedConceptSchema):
                data = model._meta.get_field(field).related_model.objects.get(code=data.code, system=data.system)
            setattr(instance, field, data)
        if user:
            if create:
                instance.created_by = user
            else:
                if user not in instance.updated_by.all():
                    instance.updated_by.add(user)
        if save:
            instance.save()
        return instance



class SchemaFactory(NinjaSchemaFactory):
    """
    A factory for creating Pydantic schemas from Django models.

    This factory is a subclass of `ninja.orm.factory.SchemaFactory` and overrides
    the `create_schema` method to generate Pydantic schemas with custom fields
    and properties.

    Attributes:
        IGNORE_FIELDS (List[str]): A list of field names to ignore when creating schemas.
    """

    IGNORE_FIELDS = ['auto_id']
    
    def create_schema(
        self,
        model: Type[DjangoModel],
        *,
        name: str = "",
        depth: int = 0,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        optional_fields: Optional[List[str]] = None,
        custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
        base_class: Type[Schema] = BaseSchema,
    ) -> Type[Schema]:
        """
        Creates a Pydantic schema from a Django model.

        This method generates a Pydantic schema class based on a given Django model
        and various configuration options. The schema can include, exclude, or modify
        certain fields from the model, and can also customize field properties.

        Args:
            model (Type[Model]): The Django model to create a schema from.
            name (str, optional): The name of the schema. Defaults to the model's name.
            depth (int, optional): The depth of relation fields to include. Defaults to 0.
            fields (Optional[List[str]], optional): Specific fields to include. Defaults to None.
            exclude (Optional[List[str]], optional): Fields to exclude. Defaults to None.
            optional_fields (Optional[List[str]], optional): Fields to make optional. Defaults to None.
            custom_fields (Optional[List[Tuple[str, Any, Any]]], optional): Custom fields to add. Defaults to None.
            base_class (Type[Schema], optional): The base class for the schema. Defaults to Schema.

        Returns:
            Type[Schema]: The generated Pydantic schema type.

        Raises:
            ConfigError: If both 'fields' and 'exclude' are set.
        """

        name = name or model.__name__
    
        if fields and exclude:
            raise ConfigError("Only one of 'fields' or 'exclude' should be set.")

        key = self.get_key(
            model, name, depth, fields, exclude, optional_fields, custom_fields
        )
        if key in self.schemas:
            return self.schemas[key]

        model_fields_list = list(self._selected_model_fields(model, fields, exclude))
        if optional_fields:
            if optional_fields == "__all__":
                optional_fields = [f.name for f in model_fields_list]

        definitions = {}
        for fld in model_fields_list:
            if fld.name in self.IGNORE_FIELDS:
                continue 
            field_name, (python_type, field_info) = get_schema_field(
                fld,
                depth=depth,
                optional=optional_fields and (fld.name in optional_fields),
            )
            definitions[field_name] = (python_type, field_info)

        if custom_fields:
            for fld_name, python_type, field_info in custom_fields:
                definitions[fld_name] = (python_type, field_info)

        if name in self.schema_names:
            name = self._get_unique_name(name)
        
        schema: Type[Schema] = create_pydantic_model(
            name,
            __base__=base_class,
            __module__=base_class.__module__,
            __validators__={},
            **definitions,
        )
        schema.__ormmodel__ = model
        self.schemas[key] = schema
        self.schema_names.add(name)
        return schema


factory = SchemaFactory()
create_schema = factory.create_schema
_is_modelschema_class_define = True

