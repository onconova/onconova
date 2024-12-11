from typing import Any,List, Tuple, Type, Optional

from django.db.models import Model as DjangoModel
from django.db.models import ManyToManyRel, ManyToOneRel, ForeignKey

from django_measurement.models import MeasurementField

from pydantic import BaseModel as PydanticBaseModel, ConfigDict

from pop.terminology.models import CodedConcept

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
        m2m_relations = {}
        if create:
            instance = model()
        serialized_data = super().model_dump(exclude_unset=True)
        for field_name, field in self.model_fields.items():
            # Skip unset fields
            if field_name not in serialized_data:
                continue
            # Get field data
            data = serialized_data[field_name]
            # Get field metadata
            field_meta = field.json_schema_extra
            if field_meta is None:
                continue
            orm_field =  model._meta.get_field(
                field_meta.get('orm_name', field.alias)
            )
            
            # Handle relational fields
            if field_meta.get('is_relation'):
                related_model = orm_field.related_model
                if field_meta.get('many_to_many') or field_meta.get('one_to_many'):
                    # Collect all related instances
                    m2m_relations[orm_field.name] = [
                        related_model.objects.get(id=item.get('id') if isinstance(item, dict) else item) for item in data
                    ]
                    # Do not set many-to-many or one-to-many fields yet
                    continue
                else:
                    if data is None:
                        related_instance = None
                    else:
                        # Handle ForeignKey fields/relations
                        if field_meta.get('expanded'):
                            # If the serialized fields has been expanded, the data already contains the data
                            related_instance = data
                        else:
                            if issubclass(related_model, CodedConcept):
                                # For coded concepts, wuery the database via the code and codesystem
                                related_instance = related_model.objects.get(code=data.get('code'), system=data.get('system'))
                            else:
                                # Otherwise, query the database via the foreign key to get the related instance
                                related_instance = related_model.objects.get(id=data)
                    # Set the related instance value into the model instance
                setattr(instance, orm_field.name, related_instance)      
            else:             
                # For measurement fields, add the measure with the provided unit and value
                if isinstance(orm_field, MeasurementField):
                    measure = orm_field.measurement
                    setattr(instance, orm_field.name, measure(**{data.get('unit'): data.get('value')}))
                else:
                    # Otherwise simply handle all other non-relational fields
                    setattr(instance, orm_field.name, data)
        # Save the model instance to the database    
        instance.save()
        # Set many-to-many
        for orm_field, related_instances in m2m_relations.items():
            getattr(instance, orm_field).set(related_instances)
        # Update the information on the requesting user        
        if user:
            if create:
                instance.created_by = user
                instance.updated_by.add(user)
            else:
                if user not in instance.updated_by.all():
                    instance.updated_by.add(user) 
        instance.save()            
        return instance


