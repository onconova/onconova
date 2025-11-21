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
