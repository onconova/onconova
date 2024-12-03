from typing import Any,List, Tuple, Type, Optional

from django.db.models import Model as DjangoModel
from django.db.models import ManyToManyRel, ManyToOneRel, ForeignKey

from pydantic import BaseModel as PydanticBaseModel, ConfigDict

from pop.core.schemas import CodedConceptSchema

def to_camel_case(string: str) -> str:
    """
    Convert a string from snake_case to camelCase.

    Args:
        string (str): The string to convert.

    Returns:
        str: The converted string.
    """
    return ''.join([
        word if n==0 else word.capitalize()
            for n,word in enumerate(string.split('_'))
    ])

class BaseSchema(PydanticBaseModel):
    """
    Expands the Pydantic [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) to use aliases by default.    
    """    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name = True,
    )

    @classmethod
    def model_validate(cls, obj=None, *args, **kwargs):
        if isinstance(obj, DjangoModel):
            data = {}
            for field in obj._meta.get_fields():
                if field.is_relation:
                    expanded =  to_camel_case(field.name) in cls.model_fields
                    if field.one_to_many or field.many_to_many:
                        data[field.name if expanded else field.name + '_ids'] = [
                            related_object if expanded else related_object.id for related_object in getattr(obj, field.name).all()
                        ]
                    else:
                        related_object =  getattr(obj, field.name)
                        if related_object:
                            data[field.name if expanded else field.name + '_id'] = related_object if expanded else related_object.id
                else:
                    data[field.name] = getattr(obj, field.name) 
            for attr_name in dir(obj.__class__):  # dir() inspects class attributes
                if not attr_name in cls.model_fields: continue
                attr = getattr(obj.__class__, attr_name, None)
                if isinstance(attr, property):  # Check if it is a property
                    data[attr_name] = getattr(obj, attr_name)

            obj = data
        return super().model_validate(obj=obj, *args, **kwargs)

    def model_dump(self, *args, **kwargs):
        """
        Override the Pydantic `model_dump` method to always use aliases and exclude None values.
        """
        kwargs.update({'exclude_none': True})
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
        kwargs.update({'exclude_none': True})
        # Call the superclass method with updated arguments
        return super().model_dump_json(*args, **kwargs)

    def model_dump_django(
            self, 
            model: Type[DjangoModel] = None, 
            instance: Optional[DjangoModel] = None, 
            user: Optional[DjangoModel]=None,
    ) -> DjangoModel:
        """
        Creates a Django model instance from the current schema.
        """
        model = model or self.__ormmodel__
        create = instance is None 
        if create:
            instance = model()
        for field_name, field in self.model_fields.items():
            data = getattr(self, field_name)
            # Handle foreign key relations through IDs
            if data and field.alias.endswith('_id'):
                fk_name = field.alias.rstrip('_ids') 
                related_model = model._meta.get_field(fk_name).related_model
                data = related_model.objects.get(id=data).pk
                
            if isinstance(data, CodedConceptSchema):
                data = model._meta.get_field(field.alias).related_model.objects.get(code=data.code, system=data.system)
            try:
                setattr(instance, field.alias, data)
            except: pass
        print('INSTANCE', self.model_dump())       
        instance.save()
        for field_name, field in self.model_fields.items():
            m2m_field_name = None
               
            if field.alias.endswith('_ids'):
                m2m_field_name = field.alias.rstrip('_ids')
            elif hasattr(model, field.alias) and model._meta.get_field(field.alias).many_to_many:
                m2m_field_name = field.alias
                
            if m2m_field_name:
                related_model = model._meta.get_field(m2m_field_name).related_model
                items = getattr(self, field_name)
                getattr(instance, m2m_field_name).set([
                    related_model.objects.get(id=item.id if hasattr(item,'id') else item) for item in items
                ])
                
        if user:
            if create:
                instance.created_by = user
                instance.updated_by.add(user)
            else:
                if user not in instance.updated_by.all():
                    instance.updated_by.add(user) 
        instance.save()            
        return instance


