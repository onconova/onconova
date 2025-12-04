from fhircraft.fhir.resources.datatypes.R4.complex import (
    Reference,
    Coding,
    CodeableConcept,
)
from onconova.core.schemas import CodedConcept


def construct_fhir_codeable_concept(concept: CodedConcept | Coding) -> CodeableConcept:
    if isinstance(concept, CodedConcept):
        return CodeableConcept(coding=[Coding.model_validate(concept.model_dump())])
    elif isinstance(concept, Coding):
        return CodeableConcept(coding=[concept])


def internal_to_ucum(unit: str):
    unit = unit.replace("__", "/")
    unit = unit.replace("IU", "[iU]")
    unit = unit.replace("square_meter", "m2")
    return unit


def ucum_to_internal(unit: str):
    unit = unit.replace("/", "__")
    unit = unit.replace("[iU]", "IU")
    unit = unit.replace("m2", "square_meter")
    return unit
