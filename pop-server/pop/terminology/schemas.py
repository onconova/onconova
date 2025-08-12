from ninja import Schema, Field
from typing import Any

class CodedConcept(Schema):
    """
    A coded concept as described by a standardized terminology
    """

    code: str = Field(
        title="Code",
        description=(
            "A symbol representing the concept, expressed in the syntax defined by the code system. "
            "This may be a simple predefined code or a more complex expression, depending on the system's capabilities (e.g., post-coordination or compositional syntax)."
        )
    )
    system: str | None = Field(
        default=None,
        title="Code System",
        description=(
            "The unique identifier (usually a canonical URL) of the code system that establishes the meaning of the code. "
            "This identifier ensures context and unambiguous interpretation of the code."
        )
    )
    display: str | None = Field(
        default=None,
        title="Display",
        description=(
            "A human-friendly rendering of the concept as defined by the code system, intended for display to end users. "
            "Display strings must adhere to the conventions and language of the code system."
        )
    )
    definition: str | None = Field(
        default=None,
        title="Definition",
        description=(
            "A formal and precise narrative description of the concept, as provided by the code system's definition."
        )
    )
    version: str | None = Field(
        default=None,
        title="Version",
        description=(
            "The specific version of the code system from which this code was selected, ensuring traceability and reproducibility."
        )
    )
    parent: str | None = Field(
        default=None,
        title="Parent Code",
        description=(
            "The code of the immediate parent concept, establishing hierarchical relationships within the code system (if applicable)."
        )
    )
    synonyms: list[str] = Field(
        default=[],
        title="Synonyms",
        description=(
            "Alternative human-readable terms or phrases for the concept, supporting a broader range of searches and user interpretations."
        )
    )
    properties: dict[str, Any] | None = Field(
        default=None,
        title="Properties",
        description=(
            "Additional attributes or metadata for the concept, as defined by the code system's property definitions. "
            "These properties capture extra information beyond the basic code, display, and definition."
        )
    )
    
    def __hash__(self):
        return hash(self.__repr__())
