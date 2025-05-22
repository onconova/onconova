
import inspect
from typing import Optional, Dict, get_args, get_origin, Type, Any, Union, Callable

from ninja import Schema, FilterSchema
from ninja.schema import DjangoGetter as BaseDjangoGetter
from pydantic import BaseModel as PydanticBaseModel, ConfigDict, model_validator
from pydantic.fields import FieldInfo

from django.db import transaction
from django.db.models import Q, QuerySet, Model as DjangoModel, Field as DjangoField
from django.contrib.postgres.fields import DateRangeField, BigIntegerRangeField

from pop.terminology.models import CodedConcept
from pop.core.measures.fields import MeasurementField
from pop.core.utils import to_camel_case 

class FilterBaseSchema(FilterSchema):
    _queryset_model: Type[DjangoModel] = None

    def filter(self, queryset: QuerySet) -> QuerySet:
        self._queryset_model = queryset.model
        filtered_queryset = queryset.filter(self.get_filter_expression())
        self._queryset_model = None
        return filtered_queryset
     
    def get_filter(self, field_name: str) -> Callable:
        method_name = f"filter_{field_name}".replace('.', '_')
        return getattr(self, method_name)

    def _resolve_field_expression(self, field_name: str, field_value: Any, field: FieldInfo) -> Q:
        field_name = field_name.replace('.', '_')
        return super()._resolve_field_expression(field_name, field_value, field)


class OrmMetadataMixin:
    __orm_model__: Type[DjangoModel] = None
    __orm_meta__: Dict[str, Type[DjangoField]] = None

    @classmethod
    def set_orm_metadata(cls, **metadata: Dict[str, DjangoField]):
        """
        Sets the ORM metadata of the class.

        The ORM metadata is a dictionary mapping field names to Django model
        fields. This method is used by the ModelSchema metaclass to set the
        ORM metadata of the class.

        Args:
            **metadata: A dictionary of keyword arguments where the key is a
                string and the value is a Django model field instance.

        Raises:
            TypeError: If the value of any keyword argument is not a Django model
                field instance.
        """
        for field in metadata.values():
            if not isinstance(field, DjangoField):
                raise TypeError('The set_orm_metadata only accepts keyword-argument pairs containing Django model field instances.')
        cls.__orm_meta__ = metadata

    @classmethod
    def get_orm_metadata(cls):
        """
        Returns a dictionary mapping field names to Django model fields.

        The dictionary is the ORM metadata of the class.

        Returns:
            A dictionary of keyword arguments where the key is a string and the
                value is a Django model field instance.
        """
        return cls.__orm_meta__

    @classmethod
    def set_orm_model(cls, model: Union[None, Type[DjangoModel]]):
        """
        Sets the ORM model class for the schema.

        This method assigns a Django model class to the schema, allowing it to
        interact with the database representation of that model. It ensures that
        the provided model is a valid Django model class.

        Args:
            model (Union[None, Type[DjangoModel]]): The Django model class to set
                as the ORM model. If None, no model is set.

        Raises:
            TypeError: If the provided model is not a Django model class.
        """
        if model is not None:
            if not isinstance(model, type) and not issubclass(model, DjangoModel):
                raise TypeError('The set_orm_model method only accept a Django model class as argument.')
        cls.__orm_model__ = model

    @classmethod
    def get_orm_model(cls):
        """
        Returns the Django model class that is associated with the schema.

        Returns:
            The Django model class associated with the schema, or None if no model
            is associated.
        """
        return cls.__orm_model__
    

class DjangoGetter(BaseDjangoGetter):
    def __getattr__(self, key: str) -> Any:
        resolver = getattr(self._schema_cls, f'resolve_{key}', None)
        if resolver and isinstance(self._obj, DjangoModel):
            params = inspect.signature(resolver).parameters
            if 'context' in params:
                value = resolver(self._obj, context=self._context)
            else:
                value = resolver(self._obj)
            return self._convert_result(value)
        else:
            return super().__getattr__(key)


class BaseSchema(Schema):
    """
    Expands the Pydantic [BaseModel](https://docs.pydantic.dev/latest/api/base_model/) to use aliases by default.    
    """    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name = True,
    )
    
    @model_validator(mode="wrap")
    @classmethod
    def _run_root_validator(cls, values, handler, info):
        forbids_extra = cls.model_config.get("extra") == "forbid"
        should_validate_assignment = cls.model_config.get("validate_assignment", False)
        if forbids_extra or should_validate_assignment:
            handler(values)
        values = DjangoGetter(values, cls, info.context)
        return handler(values)

    def model_dump(self, *args, **kwargs):
        """
        Override the Pydantic `model_dump` method to exclude `None` values.
        """
        kwargs.update({'exclude_none': True})
        return super().model_dump(*args, **kwargs)
    
    def model_dump_json(self, *args, **kwargs):
        """
        Override the Pydantic `model_dump_json` method to exclude `None` values.
        """
        # Update kwargs to use aliases and exclude None values
        kwargs.update({'exclude_none': True})
        # Call the superclass method with updated arguments
        return super().model_dump_json(*args, **kwargs)


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
        field_info = next((info for field_name, info in cls.model_fields.items() if (info.alias or field_name) == field.name), None)
        if not field_info:
            return None
        return get_model_from_type(field_info.annotation) 

    @classmethod
    def model_validate(cls, obj=None, *args, **kwargs):
        """
        Validates the given object against the Pydantic model's fields and returns
        a dictionary of validated data.

        If the object is a Django model instance, the method extracts the data
        from the model's fields and applies validation for each field. The method
        handles one-to-one, one-to-many, many-to-many, and foreign key
        relationships, as well as properties defined in the model class.

        The method also handles expansion of related fields, which allows the
        inclusion of data from related models in the validated output.

        Args:
            obj (Any): The object to validate against the Pydantic model.
            *args: Additional positional arguments passed to the Pydantic model
                validation method.
            **kwargs: Additional keyword arguments passed to the Pydantic model
                validation method.

        Returns:
            dict: A dictionary of validated data extracted from the given object.
        """
        # Check if the object is a Django model instance
        if isinstance(obj, DjangoModel):
            data = {}  # Initialize an empty dictionary to hold field data


            for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
                if name.startswith('resolve_'):
                    key = name.removeprefix('resolve_')
                    # Check if a custmom resolver has been defined for the field
                    params = inspect.signature(method).parameters
                    if 'context' in params:
                        data[key] = method(obj, context=kwargs.get('context'))
                    else:
                        data[key] = method(obj)

            # Loop over all fields in the Django model's meta options
            for field in obj._meta.get_fields():
                orm_field_name = field.name
                if orm_field_name in ['events', 'parent_events']:
                    continue
                if orm_field_name in data or to_camel_case(orm_field_name) in data:
                    continue
                # Check if the field is a relation (foreign key, many-to-many, etc.)
                if field.is_relation:
                    # Determine if the field needs expansion based on class model fields
                    related_schema = cls.extract_related_model(field)
                    expanded = related_schema is not None 
                    # Handle one-to-many or many-to-many relationships
                    if field.one_to_many or field.many_to_many:
                        if expanded:
                            data[orm_field_name] = cls._resolve_expanded_many_to_many(obj, orm_field_name, related_schema)
                        else:
                            data[orm_field_name] = cls._resolve_many_to_many(obj, orm_field_name)
                    else:
                        # Handle one-to-one or foreign key relationships
                        related_object = getattr(obj, orm_field_name)
                        if related_object:
                            if expanded:
                                # Validate the related object if expansion is needed
                                data[orm_field_name] = cls._resolve_expanded_foreign_key(obj, orm_field_name, related_schema)
                            else:
                                # Otherwise, just get the ID of the related object
                                data[orm_field_name] = cls._resolve_foreign_key(obj, orm_field_name)
                else:
                    # For measurement fields, add the measure with the provided unit and value
                    if isinstance(field, MeasurementField):
                        data[orm_field_name] = cls._resolve_measure(obj, orm_field_name)
                    else:
                        # For non-relation fields, simply get the attribute value
                        data[orm_field_name] = getattr(obj, orm_field_name)

            # Inspect class attributes to handle properties
            for attr_name in dir(obj.__class__):
                # Skip attributes not defined in the model fields
                if not to_camel_case(attr_name) in cls.model_fields and not to_camel_case(attr_name) in [field.alias for field in cls.model_fields.values()]:
                    continue

                # Get the attribute from the class
                attr = getattr(obj.__class__, attr_name, None)
                # If the attribute is a property, get its value
                if isinstance(attr, property):
                    data[attr_name] = getattr(obj, attr_name)

            # Replace obj with the constructed data dictionary
            obj = data
        # Call the superclass model_validate method with the constructed data
        return super().model_validate(obj=obj, *args, **kwargs)

    @staticmethod
    def _resolve_foreign_key(obj, orm_field_name):
        if not getattr(obj, orm_field_name, None):
            return None         
        return getattr(obj, orm_field_name).id

    @staticmethod
    def _resolve_expanded_foreign_key(obj, orm_field_name, related_schema):
        if not getattr(obj, orm_field_name, None):
            return None 
        return  related_schema.model_validate(getattr(obj, orm_field_name))

    @staticmethod
    def _resolve_expanded_many_to_many(obj, orm_field_name, related_schema):
        if not getattr(obj, orm_field_name, None):
            return [] 
        # Collect related objects and apply validation or get their IDs
        return [related_schema.model_validate(related_object) for related_object in getattr(obj, orm_field_name).all()]
    
    @staticmethod
    def _resolve_many_to_many(obj, orm_field_name):
        if not getattr(obj, orm_field_name, None):
            return [] 
        # Collect related objects and apply validation or get their IDs
        return [related_object.id for related_object in getattr(obj, orm_field_name).all()]

    @staticmethod
    def _resolve_measure(obj, orm_field_name):
        from pop.core.measures.schemas import Measure
        if not getattr(obj, orm_field_name, None):
            return None
        
        measure = getattr(obj, orm_field_name)
        default_unit = obj._meta.get_field(orm_field_name).get_default_unit()
        return Measure(
            value=measure if isinstance(measure, (float, int)) else getattr(measure, default_unit),
            unit=default_unit
        )

    def model_dump_django(self, 
            model: Optional[Type[DjangoModel]] = None, 
            instance: Optional[DjangoModel] = None, 
            create: Optional[bool] = None
        ) -> DjangoModel:
        """
        Converts a Pydantic model instance to a Django model instance, handling
        both relational and non-relational fields.

        This method maps the fields of a Pydantic model to a corresponding Django
        model instance, managing the creation or updating of related instances 
        for many-to-many, one-to-many, and foreign key relationships. It also 
        handles custom fields like measurement and range fields.

        Args:
            model (Optional[Type[DjangoModel]]): The Django model class to use. 
                Defaults to the schema's ORM model.
            instance (Optional[DjangoModel]): The existing Django model instance 
                to update. If None, a new instance is created.
            user (Optional[DjangoModel]): The user associated with the operation,
                used for setting created_by and updated_by fields.
            create (Optional[bool]): Whether to create a new instance. Defaults to
                True if no instance is provided.

        Returns:
            DjangoModel: The populated Django model instance.
        """
        model = model or self.get_orm_model()
        create = create if create is not None else instance is None 
        m2m_relations, o2m_relations = {}, {}
        if create and instance is None:
            instance = model()
        if instance and not isinstance(instance, model):
            old_instace = instance
            instance = model()
            instance.pk = old_instace.pk
            old_instace.delete()

        serialized_data = super().model_dump()
        for field_name, field in self.model_fields.items():
            # Skip unset fields
            if field_name not in serialized_data or field_name=='password':
                continue
            # Get field data
            data = serialized_data[field_name]
            # Get field metadata
            orm_field = self.get_orm_metadata().get(field_name)
            if orm_field is None:
                continue
            # Handle relational fields
            if orm_field.is_relation:
                related_model = orm_field.related_model
                if orm_field.many_to_many:
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
                elif orm_field.one_to_many:
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
                        if field.json_schema_extra.get('x-expanded'):
                            # If the serialized fields has been expanded, the data already contains the data
                            related_instance = data
                        else:
                            if issubclass(related_model, CodedConcept):
                                # For coded concepts, wuery the database via the code and codesystem
                                related_instance = related_model.objects.get(code=data.get('code'), system=data.get('system'))
                            else:
                                # Otherwise, query the database via the foreign key to get the related instance
                                print('DATA', type(data), data)
                                related_instance = related_model.objects.get(id=data.get('id') if isinstance(data, dict) else data)
                # Set the related instance value into the model instance
                setattr(instance, orm_field.name, related_instance)      
            else:             
                # For measurement fields, add the measure with the provided unit and value
                if isinstance(orm_field, MeasurementField) and data is not None:
                    setattr(instance, orm_field.name,  orm_field.measurement(**{data.get('unit'): data.get('value')}))
                elif isinstance(orm_field, (DateRangeField, BigIntegerRangeField)) and data is not None:
                    setattr(instance, orm_field.name, (data['start'], data['end']))
                else:
                    # Otherwise simply handle all other non-relational fields
                    setattr(instance, orm_field.name, data)

        # Rollback changes if any exception occurs during the transaction
        with transaction.atomic():
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
                    related_schema.model_validate(entry).model_dump_django(instance=related_instance)            
        return instance


class ModelFilterSchema(BaseSchema):

    @classmethod
    def get_django_lookup(cls, filter_name):
        filter_info = cls.model_fields.get(filter_name)
        return filter_info.json_schema_extra.get('django_lookup')


