import inspect
from typing import (
    Any,
    Callable,
    ClassVar,
    Mapping,
    Optional,
    Type,
    TypeVar,
    get_args,
    get_origin,
)

from django.contrib.postgres.fields import BigIntegerRangeField, DateRangeField
from django.db import transaction
from django.db.models import Field as DjangoField
from django.db.models import Model as DjangoModel
from ninja import Schema
from ninja.schema import DjangoGetter as BaseDjangoGetter
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, model_validator

from onconova.core.auth.models import User
from onconova.core.measures.fields import MeasurementField
from onconova.core.models import BaseModel, UntrackedBaseModel
from onconova.core.utils import to_camel_case
from onconova.terminology.models import CodedConcept

_DjangoModel = TypeVar("_DjangoModel", bound=DjangoModel)


class BaseSchema(Schema):
    """
    
    A base schema class that extends Pydantic's Schema class to provide seamless integration between
    Pydantic models and Django ORM models, with support for serialization and deserialization.

    This class provides functionality to:
    - Map Django model fields to Pydantic schema fields
    - Handle relationships (one-to-one, one-to-many, many-to-many)
    - Support custom field resolution
    - Manage ORM metadata and model associations
    - Handle measurement fields and coded concepts
    - Process Django model properties

    Attributes:
        __orm_model__ (ClassVar[Type[UntrackedBaseModel]]): The associated Django model class
        __orm_meta__ (ClassVar[Mapping[str, DjangoField]]): Mapping of field names to Django field instances

    Example:
        ```python
        class UserSchema(BaseSchema):
            id: int
            username: str
            email: str

            class Config:
                from_attributes = True

            def __init_subclass__(cls):
                cls.set_orm_model(User)
                cls.set_orm_metadata(
                    id=User._meta.get_field('id'),
                    username=User._meta.get_field('username'),
                    email=User._meta.get_field('email')
        ```
    """

    # Pydantic model configuration
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    __orm_model__: ClassVar[Type[UntrackedBaseModel]]
    __orm_meta__: ClassVar[Mapping[str, DjangoField]]

    @classmethod
    def set_orm_metadata(cls, **metadata: DjangoField) -> None:
        """
        Sets ORM metadata for the class using Django model field instances.

        This class method allows setting metadata for ORM operations by associating Django model fields
        with the class. The metadata is stored in the `__orm_meta__` class attribute.

        Args:
            **metadata (DjangoField): Keyword arguments where each value must be a Django model field instance.

        Raises:
            TypeError: If any of the provided metadata values is not a Django model field instance.
        """
        for field in metadata.values():
            if not isinstance(field, DjangoField):
                raise TypeError(
                    "The set_orm_metadata only accepts keyword-argument pairs containing Django model field instances."
                )
        cls.__orm_meta__ = metadata

    @classmethod
    def get_orm_metadata(cls):
        """
        Retrieves the ORM metadata associated with the class.

        Returns:
            (dict): A dictionary containing the ORM metadata information stored in the __orm_meta__ attribute. This metadata typically includes configuration for database mapping and relationships.
        """
        return cls.__orm_meta__

    @classmethod
    def set_orm_model(cls, model: Type[UntrackedBaseModel] | Type[BaseModel]) -> None:
        """Sets the ORM model class for the serializer.

        This class method associates a Django model class with the serializer, enabling direct
        model-serializer mapping for database operations.

        Args:
            model (Type[UntrackedBaseModel] | Type[BaseModel]): The Django model class to be
                associated with the serializer. Must be a subclass of either UntrackedBaseModel
                or BaseModel.

        Raises:
            TypeError: If the provided model is not a valid Django model class (not a subclass
                of UntrackedBaseModel or BaseModel).

        Note:
            This method modifies the `__orm_model__` class attribute of the serializer class.
        """
        if model is not None:
            if not isinstance(model, type) and not issubclass(
                model, (UntrackedBaseModel, BaseModel)
            ):
                raise TypeError(
                    "The set_orm_model method only accept a ONCONOVA Django model class as argument."
                )
        cls.__orm_model__ = model

    @classmethod
    def get_orm_model(cls):
        """
        Retrieves the ORM model class associated with this serializer.

        Returns:
            (type): The ORM model class that this serializer is mapped to.
                This is typically defined as the __orm_model__ class attribute.
        """
        return cls.__orm_model__

    @model_validator(mode="wrap")
    @classmethod
    def _run_root_validator(cls, values, handler, info):
        """
        Applies DjangoGetter to resolve dynamic field values during validation.

        Args:
            values (dict): The values to be validated.
            handler (Callable): The next validation handler in the chain.
            info (ValidationInfo): Additional validation context information.
        """
        forbids_extra = cls.model_config.get("extra") == "forbid"
        should_validate_assignment = cls.model_config.get("validate_assignment", False)
        if forbids_extra or should_validate_assignment:
            handler(values)
        values = DjangoGetter(values, cls, info.context)
        return handler(values)

    def model_dump(self, *args, **kwargs):
        """
        Override the default model_dump method to exclude None values by default.

        This method enhances the base model_dump functionality by setting 'exclude_none=True'
        as a default parameter, ensuring that fields with None values are not included in the
        output dictionary.

        Args:
            args (list): Variable length argument list to pass to parent model_dump.
            kwargs (dict): Arbitrary keyword arguments to pass to parent model_dump.

        Returns:
            (dict): A dictionary representation of the model with None values excluded by default.
        """
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs):
        """
        Override the Pydantic `model_dump_json` method to exclude `None` values by default,
        unless the caller explicitly provides a value for `exclude_none`.
        """
        # Only set exclude_none if not already provided by the caller
        kwargs.setdefault("exclude_none", True)
        return super().model_dump_json(*args, **kwargs)

    @classmethod
    def model_validate(cls, obj=None, *args, **kwargs):
        """
        Validates and converts a Django model instance into a schema-compliant dictionary.

        This class method handles the conversion of Django model instances into a format that can be
        validated by the schema. It processes various field types including:
        - Regular model fields
        - Foreign keys and related fields
        - Many-to-many relationships
        - Custom property fields
        - Measurement fields
        - Custom resolver methods (prefixed with 'resolve_')

        Args:
            obj (Optional[DjangoModel]): The Django model instance to validate
            args (list): Additional positional arguments passed to the parent validator
            kwargs (dict): Additional keyword arguments passed to the parent validator

        Returns:
            (Any): The validated model instance converted to the schema format

        Raises:
            NotImplementedError: If the superclass doesn't implement a custom `model_validate` method

        Notes:
            - Custom field resolvers should be defined as methods prefixed with 'resolve_'
            - Resolver methods can optionally accept a context parameter
            - The method skips processing of 'events' and 'parent_events' fields
            - Field names are converted to camelCase in the output
            - The superclass must implement a custom `model_validate` method (e.g., inherit from Pydantic's BaseModel)
        """
        # Check if the object is a Django model instance
        if isinstance(obj, DjangoModel):
            data = {}  # Initialize an empty dictionary to hold field data

            for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
                if name.startswith("resolve_"):
                    key = name.removeprefix("resolve_")
                    # Check if a custom resolver has been defined for the field
                    params = inspect.signature(method).parameters
                    if "context" in params:
                        data[key] = method(obj, context=kwargs.get("context"))
                    else:
                        data[key] = method(obj)

            # Loop over all fields in the Django model's meta options
            for field in obj._meta.get_fields():
                orm_field_name = field.name
                if orm_field_name in ["events", "parent_events"]:
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
                        if field.related_model is User:
                            data[orm_field_name] = cls._resolve_user(
                                obj, orm_field_name, many=True
                            )
                        elif expanded:
                            data[orm_field_name] = cls._resolve_expanded_many_to_many(
                                obj, orm_field_name, related_schema
                            )
                        else:
                            data[orm_field_name] = cls._resolve_many_to_many(
                                obj, orm_field_name
                            )
                    else:
                        # Handle one-to-one or foreign key relationships
                        related_object = getattr(obj, orm_field_name, None)
                        if related_object:
                            if field.related_model is User:
                                data[orm_field_name] = cls._resolve_user(
                                    obj, orm_field_name
                                )
                            elif expanded:
                                # Validate the related object if expansion is needed
                                data[orm_field_name] = (
                                    cls._resolve_expanded_foreign_key(
                                        obj, orm_field_name, related_schema
                                    )
                                )
                            else:
                                # Otherwise, just get the ID of the related object
                                data[orm_field_name] = cls._resolve_foreign_key(
                                    obj, orm_field_name
                                )
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
                camel_attr = to_camel_case(attr_name)
                in_model_fields = camel_attr in cls.model_fields
                in_aliases = camel_attr in [
                    field.alias for field in cls.model_fields.values()
                ]
                if not in_model_fields and not in_aliases:
                    continue

                # Get the attribute from the class
                attr = getattr(obj.__class__, attr_name, None)
                # If the attribute is a property, get its value
                # If the attribute is a property, get its value
                if isinstance(attr, property):
                    # Map the property name to the schema field name or alias
                    for field_name, field_info in cls.model_fields.items():
                        if to_camel_case(attr_name) == to_camel_case(field_name) or (
                            field_info.alias
                            and to_camel_case(attr_name)
                            == to_camel_case(field_info.alias)
                        ):
                            data[field_info.alias or field_name] = getattr(
                                obj, attr_name
                            )
                            break
            # Replace obj with the constructed data dictionary
            obj = data

        # Call the superclass model_validate method with the constructed data
        # NOTE: The superclass must implement a custom `model_validate` method (e.g., Pydantic's BaseModel).
        # Otherwise, this may result in recursion.
        base_model_validate = getattr(super(), "model_validate", None)
        if (
            base_model_validate is None
            or base_model_validate is BaseSchema.model_validate
        ):
            raise NotImplementedError(
                "The superclass must implement a custom `model_validate` method (e.g., inherit from Pydantic's BaseModel)."
            )
        return base_model_validate(obj=obj, *args, **kwargs)

    def model_dump_django(
        self,
        model: Optional[Type[_DjangoModel]] = None,
        instance: Optional[_DjangoModel] = None,
        create: Optional[bool] = None,
        **fields,
    ) -> _DjangoModel:
        """
        Serializes the current schema instance and applies its data to a Django model instance.

        This method handles both the creation of new model instances and updating existing ones.
        It supports relational fields (ForeignKey, ManyToMany, OneToMany), measurement fields, and range fields.
        Relational fields are resolved and set appropriately, including expanded data for related instances.
        Many-to-many and one-to-many relationships are set after the main instance is saved, within a database transaction.

        Args:
            model (Optional[Type[_DjangoModel]]): The Django model class to use. If not provided, attempts to retrieve from schema.
            instance (Optional[_DjangoModel]): An existing Django model instance to update. If not provided, a new instance is created.
            create (Optional[bool]): Whether to create a new instance. If None, determined by presence of `instance`.
            fields (dict): Additional field values to set on the model instance.

        Returns:
            (_DjangoModel): The saved Django model instance with all fields and relationships set.

        Raises:
            ValueError: If no model is provided or found, or if no instance is provided or created.
        """

        m2m_relations: dict[str, list[DjangoModel]] = {}
        o2m_relations: dict[DjangoField, dict] = {}
        get_orm_model: Callable = getattr(self, "get_orm_model", lambda: None)
        get_orm_metadata: Callable = getattr(self, "get_orm_metadata", lambda: {})
        model = model or get_orm_model()
        if model is None:
            raise ValueError("No model provided or found in schema.")
        create = create if create is not None else instance is None
        if create and instance is None:
            instance = model()
        if instance and not isinstance(instance, model):
            old_instance: DjangoModel = instance
            instance = model()
            instance.pk = old_instance.pk
            instance.save()
            old_instance.delete()
        if not instance:
            raise ValueError("No instance provided or created.")
        serialized_data = super().model_dump()
        for field_name, field in self.model_fields.items():
            # Skip unset fields
            if field_name not in serialized_data or field_name == "password":
                continue
            # Get field data
            data = serialized_data[field_name]
            # Get field metadata
            orm_field: DjangoField = get_orm_metadata().get(field_name)
            if orm_field is None:
                continue
            # Handle relational fields
            if orm_field.is_relation and orm_field.related_model:
                related_model: Type[DjangoModel] = orm_field.related_model
                if orm_field.many_to_many:
                    if issubclass(related_model, CodedConcept):
                        # Collect all related instances
                        m2m_relations[orm_field.name] = [
                            related_model.objects.get(
                                code=concept.get("code"), system=concept.get("system")
                            )
                            for concept in data or []
                        ]
                    elif issubclass(related_model, User):
                        # For users. query the database via the username
                        m2m_relations[orm_field.name] = [
                            related_model.objects.get(username=username)
                            for username in data or []
                        ]
                    else:
                        # Collect all related instances
                        m2m_relations[orm_field.name] = [
                            related_model.objects.get(
                                id=item.get("id") if isinstance(item, dict) else item
                            )
                            for item in data or []
                        ]
                    # Do not set many-to-many or one-to-many fields yet
                    continue
                elif orm_field.one_to_many:
                    args = get_args(field.annotation)
                    related_schema = args[0] if args else None
                    # Collect all related instances
                    o2m_relations[orm_field] = {
                        "schema": related_schema,
                        "entries": data,
                    }
                    # Do not set many-to-many or one-to-many fields yet
                    continue
                else:
                    if data is None:
                        related_instance = None
                    else:
                        # Handle ForeignKey fields/relations
                        if field.json_schema_extra and field.json_schema_extra.get(
                            "x-expanded"
                        ):
                            # The data is already expanded and contains the related instance data
                            related_instance = data
                        else:
                            if issubclass(related_model, CodedConcept):
                                # For coded concepts, query the database via the code and codesystem
                                related_instance = related_model.objects.get(
                                    code=data.get("code"), system=data.get("system")
                                )
                            elif issubclass(related_model, User):
                                # For users. query the database via the username
                                related_instance = related_model.objects.get(
                                    username=data
                                )
                            else:
                                # Otherwise, query the database via the foreign key to get the related instance
                                related_instance = related_model.objects.get(
                                    id=(
                                        data.get("id")
                                        if isinstance(data, dict)
                                        else data
                                    )
                                )
                # Set the related instance value into the model instance
                setattr(instance, orm_field.name, related_instance)
            else:
                # For measurement fields, add the measure with the provided unit and value
                if isinstance(orm_field, MeasurementField) and data is not None:
                    setattr(
                        instance,
                        orm_field.name,
                        orm_field.measurement(**{data.get("unit"): data.get("value")}),
                    )
                elif (
                    isinstance(orm_field, (DateRangeField, BigIntegerRangeField))
                    and data is not None
                ):
                    setattr(instance, orm_field.name, (data["start"], data["end"]))
                else:
                    # Otherwise simply handle all other non-relational fields
                    setattr(instance, orm_field.name, data)

        for orm_field_name, value in fields.items():
            setattr(instance, orm_field_name, value)

        # Rollback changes if any exception occurs during the transaction
        with transaction.atomic():
            # Save the model instance to the database
            instance.save()
            # Set many-to-many
            for orm_field_name, related_instances in m2m_relations.items():
                getattr(instance, orm_field_name).set(related_instances)
            # Set one-to-many
            for orm_field, data in o2m_relations.items():
                related_schema = data["schema"]
                for entry in data["entries"]:
                    related_instance = orm_field.related_model(
                        **{f"{orm_field.name}": instance}
                    )  # type: ignore
                    related_schema.model_validate(entry).model_dump_django(
                        instance=related_instance
                    )
        return instance

    @staticmethod
    def _resolve_foreign_key(obj, orm_field_name):
        if not getattr(obj, orm_field_name, None):
            return None
        return getattr(obj, orm_field_name).id

    @staticmethod
    def _resolve_expanded_foreign_key(obj, orm_field_name, related_schema):
        if not getattr(obj, orm_field_name, None):
            return None
        return related_schema.model_validate(getattr(obj, orm_field_name))

    @staticmethod
    def _resolve_expanded_many_to_many(obj, orm_field_name, related_schema):
        if not getattr(obj, orm_field_name, None):
            return []
        # Collect related objects and apply validation or get their IDs
        return [
            related_schema.model_validate(related_object)
            for related_object in getattr(obj, orm_field_name).all()
        ]

    @staticmethod
    def _resolve_many_to_many(obj, orm_field_name):
        if not getattr(obj, orm_field_name, None):
            return []
        # Collect related objects and apply validation or get their IDs
        return [
            related_object.id for related_object in getattr(obj, orm_field_name).all()
        ]

    @staticmethod
    def _resolve_measure(obj, orm_field_name):
        from onconova.core.measures.schemas import Measure

        if not getattr(obj, orm_field_name, None):
            return None

        measure = getattr(obj, orm_field_name)
        default_unit = obj._meta.get_field(orm_field_name).get_default_unit()
        return Measure(
            value=(
                measure
                if isinstance(measure, (float, int))
                else getattr(measure, default_unit)
            ),
            unit=default_unit,
        )

    @staticmethod
    def _resolve_user(obj, orm_field_name, many=False):
        if not getattr(obj, orm_field_name, None):
            return []
        # Collect related objects and apply validation or get their IDs
        if many:
            return [
                related_object.username
                for related_object in getattr(obj, orm_field_name).all()
            ]
        else:
            return getattr(obj, orm_field_name).username

    @classmethod
    def extract_related_model(cls, field) -> Optional[Type[PydanticBaseModel]]:
        """
        Extracts the related Pydantic model from a FieldInfo object.

        Args:
            field (FieldInfo): A Pydantic FieldInfo object to analyze.

        Returns:
            (Optional[Type[PydanticBaseModel]]): The related Pydantic model, or None if no model is found.
        """

        def get_model_from_type(typ: Any) -> Optional[Type[PydanticBaseModel]]:
            origin = get_origin(typ)
            if origin is not None:  # If the type is a generic like List or Optional
                for arg in get_args(typ):
                    model = get_model_from_type(arg)
                    if model:
                        return model
            elif isinstance(typ, type) and issubclass(
                typ, PydanticBaseModel
            ):  # Base case: direct Pydantic model
                return typ
            return None

        matched_field_info = next(
            (
                info
                for field_name, info in cls.model_fields.items()
                if hasattr(field, "name") and (info.alias or field_name) == field.name
            ),
            None,
        )
        if not matched_field_info:
            return None
        return get_model_from_type(matched_field_info.annotation)


class DjangoGetter(BaseDjangoGetter):
    def __getattr__(self, key: str) -> Any:
        resolver = getattr(self._schema_cls, f"resolve_{key}", None)
        if resolver and isinstance(self._obj, DjangoModel):
            params = inspect.signature(resolver).parameters
            if "context" in params:
                value = resolver(self._obj, context=self._context)
            else:
                value = resolver(self._obj)
            return self._convert_result(value)
        else:
            return super().__getattr__(key)
