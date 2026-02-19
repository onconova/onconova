from ninja import Schema
from django.db.models import Model
from django.template.exceptions import TemplateSyntaxError
from typing import Any, ClassVar, Dict, List, Optional
from onconova.core.serialization.base import BaseSchema, DjangoGetter
from fhircraft.fhir.resources.base import FHIRBaseModel
from fhircraft.fhir.resources.datatypes.R4.complex import Narrative, Coding
from pydantic import model_validator
from dataclasses import dataclass


@dataclass
class MappingRule:
    """Represents a bidirectional mapping rule between internal and FHIR values."""

    internal_value: Any
    fhir_value: Any
    description: Optional[str] = None


class MappingRegistry:
    """Registry for managing bidirectional mappings between internal and FHIR values."""

    def __init__(self):
        self._mappings: Dict[str, List[MappingRule]] = {}

    def get_rules(self, mapping_name: str) -> List[MappingRule]:
        """Convert internal value to FHIR value."""
        return self._mappings.get(mapping_name, [])

    def register(self, mapping_name: str, rules: List[MappingRule]):
        """Register a set of mapping rules."""
        self._mappings[mapping_name] = rules

    def to_fhir(self, mapping_name: str, internal_value: Any) -> Any:
        """Convert internal value to FHIR value."""
        rules = self.get_rules(mapping_name)
        for rule in rules:
            if rule.internal_value == internal_value:
                return rule.fhir_value

        if internal_value is None:
            return None

        raise KeyError(f"No FHIR mapping found for {mapping_name}: {internal_value}")

    def to_internal(self, mapping_name: str, fhir_value: Any) -> Any:
        """Convert FHIR value to internal value."""
        rules = self.get_rules(mapping_name)

        # Handle None/empty cases
        if fhir_value is None:
            # Return the default for the mapping if available
            defaults = [
                rule.internal_value
                for rule in rules
                if hasattr(rule.internal_value, "UNKNOWN")
            ]
            return defaults[0] if defaults else None

        # For Coding objects, compare by code and system
        if isinstance(fhir_value, Coding):
            for rule in rules:
                if (
                    isinstance(rule.fhir_value, Coding)
                    and rule.fhir_value.code == fhir_value.code
                    and rule.fhir_value.system == fhir_value.system
                ):
                    return rule.internal_value
        else:
            for rule in rules:
                if rule.fhir_value == fhir_value:
                    return rule.internal_value

        raise KeyError(f"No internal mapping found for {mapping_name}: {fhir_value}")


class OnconovaFhirBaseSchema(BaseSchema, alias_generator=None):

    __model__: ClassVar[type[Model]]
    __schema__: ClassVar[type[BaseSchema]]
    __registry__: ClassVar[MappingRegistry] = MappingRegistry()

    @classmethod
    def get_orm_model(cls, obj: FHIRBaseModel):
        return cls.__model__

    @classmethod
    def get_orm_schema(cls, obj):
        return cls.__schema__

    @classmethod
    def map_to_fhir(cls, map: str, value: Any):
        return cls.__registry__.to_fhir(map, value)

    @classmethod
    def map_to_internal(cls, map: str, value: Any):
        return cls.__registry__.to_internal(map, value)

    @classmethod
    def register_mapping(cls, mapping_name: str, rules: List[MappingRule]):
        return cls.__registry__.register(mapping_name, rules)

    @classmethod
    def fhir_to_onconova(cls, obj: "OnconovaFhirBaseSchema") -> BaseSchema:
        raise NotImplementedError("Subclasses must implement fhir_to_onconova method")

    @classmethod
    def onconova_to_fhir(cls, obj: BaseSchema) -> "OnconovaFhirBaseSchema":
        raise NotImplementedError("Subclasses must implement onconova_to_fhir method")

    @classmethod
    def fhir_to_onconova_related(
        cls, obj: "OnconovaFhirBaseSchema"
    ) -> list[tuple[Model, BaseSchema]]:
        return []

    @model_validator(mode="before")
    @classmethod
    def pre_validator(cls, obj):
        try:
            if isinstance(obj, cls.__model__):
                obj = cls.get_orm_schema(obj).model_validate(obj)
            if isinstance(obj, DjangoGetter) and isinstance(obj._obj, cls.__model__):
                obj = cls.get_orm_schema(obj).model_validate(obj)
                return cls.onconova_to_fhir(obj)
            elif isinstance(obj, cls.get_orm_schema(obj)):
                return cls.onconova_to_fhir(obj)
        except TemplateSyntaxError:
            pass
        return obj
