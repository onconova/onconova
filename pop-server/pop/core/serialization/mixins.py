from typing import Dict, Type, Union
from django.db.models import Model as DjangoModel, Field as DjangoField


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
                raise TypeError(
                    "The set_orm_metadata only accepts keyword-argument pairs containing Django model field instances."
                )
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
                raise TypeError(
                    "The set_orm_model method only accept a Django model class as argument."
                )
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
