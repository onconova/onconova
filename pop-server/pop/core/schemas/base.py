from typing import Any,List, Tuple, Type, Optional

from django.db.models import Model as DjangoModel

from pydantic import BaseModel as PydanticBaseModel, ConfigDict

from pop.core.schemas import CodedConceptSchema 

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


