from django.db.models import Model as DjangoModel
from django.contrib.postgres.fields import DateRangeField, BigIntegerRangeField

from pop.core.fields import MeasurementField
from pop.core.utils import to_camel_case 
from pydantic import BaseModel as PydanticBaseModel, ConfigDict
from typing import Optional, List, get_args, get_origin, Type, Any

from ninja.params import Query
from django.db.models.query import QuerySet

from pop.terminology.models import CodedConcept



class FiltersBaseSchema(PydanticBaseModel):

    def apply_filters(self, queryset: QuerySet):
        print(self.__class__.__name__)
        for filter_name, filter_value in self.model_dump().items():
            if not filter_value:
                continue
            filter_info = self.model_fields.get(filter_name)
            lookup = filter_info.json_schema_extra.get('django_lookup')
            if lookup:
                queryset = queryset.filter(**{lookup: filter_value})
        return queryset


class BaseSchema(PydanticBaseModel):
    """
    Expands the Pydantic [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) to use aliases by default.    
    """    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name = True,
    )

    @classmethod
    def extract_related_model(cls,field) -> Optional[Type[PydanticBaseModel]]:
        """
        Extracts the related Pydantic model from a FieldInfo object.
        
        Args:
            field_info (FieldInfo): A Pydantic FieldInfo object to analyze.
        
        Returns:
            Optional[Type[BaseModel]]: The related Pydantic model, or None if no model is found.
        """
        def get_model_from_type(typ: Any) -> Optional[Type[PydanticBaseModel]]:
            origin = get_origin(typ)
            if origin is not None:  # If the type is a generic like List or Optional
                for arg in get_args(typ):
                    model = get_model_from_type(arg)
                    if model:
                        return model
            elif isinstance(typ, type) and issubclass(typ, PydanticBaseModel):  # Base case: direct Pydantic model
                return typ
            return None
        field_info = cls.model_fields.get(to_camel_case(field.name))
        return get_model_from_type(field_info.annotation)

    @classmethod
    def model_validate(cls, obj=None, *args, **kwargs):
        if isinstance(obj, DjangoModel):
            data = {}
            for field in obj._meta.get_fields():
                if field.is_relation:
                    expanded =  to_camel_case(field.name) in cls.model_fields
                    if field.one_to_many or field.many_to_many:
                        data[field.name if expanded else field.name + '_ids'] = [
                            cls.extract_related_model(field).model_validate(related_object) if expanded else related_object.id for related_object in getattr(obj, field.name).all()
                        ]
                    else:
                        related_object =  getattr(obj, field.name)
                        if related_object:
                            if expanded:
                                data[field.name] = cls.extract_related_model(field).model_validate(related_object)
                            else:
                                data[field.name + '_id'] = related_object.id
                else:
                    data[field.name] = getattr(obj, field.name) 
            for attr_name in dir(obj.__class__):  # dir() inspects class attributes
                if not to_camel_case(attr_name) in cls.model_fields: continue
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
            create: Optional[bool] = None,
    ) -> DjangoModel:
        """
        Creates a Django model instance from the current schema.
        """
        model = model or self.__ormmodel__
        create = create if create is not None else instance is None 
        m2m_relations = {}
        o2m_relations = {}
        if create and instance is None:
            instance = model()
        serialized_data = super().model_dump()
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
                if field_meta.get('many_to_many'):
                    if issubclass(related_model, CodedConcept): 
                        # Collect all related instances
                        m2m_relations[orm_field.name] = [
                            related_model.objects.get(code=concept.get('code'), system=concept.get('system')) for concept in data or []
                        ]
                    else:
                        # Collect all related instances
                        m2m_relations[orm_field.name] = [
                            related_model.objects.get(id=item.get('id') if isinstance(item, dict) else item) for item in data or []
                        ]
                    # Do not set many-to-many or one-to-many fields yet
                    continue
                elif field_meta.get('one_to_many'):
                    related_schema = field.annotation.__args__[0]
                    # Collect all related instances
                    o2m_relations[orm_field] = {'schema': related_schema, 'entries': data }
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
                if isinstance(orm_field, MeasurementField) and data is not None:
                    measure = orm_field.measurement
                    setattr(instance, orm_field.name, measure(**{data.get('unit'): data.get('value')}))
                elif isinstance(orm_field, (DateRangeField, BigIntegerRangeField)) and data is not None:
                    setattr(instance, orm_field.name, (data['start'], data['end']))
                else:
                    # Otherwise simply handle all other non-relational fields
                    setattr(instance, orm_field.name, data)
        # Save the model instance to the database    
        instance.save()
        # Set many-to-many
        for orm_field_name, related_instances in m2m_relations.items():
            getattr(instance, orm_field_name).set(related_instances)
        # Set one-to-many
        for orm_field, data in o2m_relations.items():
            related_schema = data['schema']
            for entry in data['entries']:               
                related_instance = orm_field.related_model(**{f'{orm_field.field.name}': instance})
                related_schema.model_validate(entry).model_dump_django(instance=related_instance, user=user)
                
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


