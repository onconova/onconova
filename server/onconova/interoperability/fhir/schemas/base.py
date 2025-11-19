from ninja import Schema
from django.db.models import Model
from typing import ClassVar
from onconova.core.serialization.base import BaseSchema, DjangoGetter
from fhircraft.fhir.resources.base import FHIRBaseModel
from pydantic import model_validator


class OnconovaFhirBaseSchema(BaseSchema):

    __model__: ClassVar[type[Model]]
    __schema__: ClassVar[type[Schema]]

    @classmethod
    def fhir_to_onconova(cls, obj: FHIRBaseModel) -> Schema:
        raise NotImplementedError("Subclasses must implement fhir_to_onconova method")

    @classmethod
    def onconova_to_fhir(cls, obj: Schema) -> FHIRBaseModel:
        raise NotImplementedError("Subclasses must implement onconova_to_fhir method")

    @model_validator(mode="before")
    @classmethod
    def pre_validator(cls, obj):
        if isinstance(obj, cls.__model__):
            obj = cls.__schema__.model_validate(obj)
        if isinstance(obj, DjangoGetter) and isinstance(obj._obj, cls.__model__):
            obj = cls.__schema__.model_validate(obj)
            return cls.onconova_to_fhir(obj)
        elif isinstance(obj, cls.__schema__):
            return cls.onconova_to_fhir(obj)
        return obj
