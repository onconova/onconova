"""
This module defines Pydantic models for FHIR CodeSystem and ValueSet resources,
enabling validation and serialization of terminology data according to the FHIR specification.
"""


from typing import List, Optional, Any, Literal
from pydantic import BaseModel, Field, RootModel

class Coding(BaseModel):
    """
    Represents a FHIR Coding element, which specifies a coded value from a terminology system.

    Attributes:
        system (Optional[str]): The identification of the code system that defines the meaning of the symbol.
        version (Optional[str]): The version of the code system which was used when choosing this code.
        code (Optional[str]): The actual code defined by the code system.
        display (Optional[str]): A human-readable representation of the code.
        userSelected (Optional[bool]): Indicates that this coding was chosen directly by the user.
    """
    system: Optional[str] = None
    version: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None
    userSelected: Optional[bool] = None

class CodeSystemConceptDesignation(BaseModel):
    """
    Represents a designation for a concept within a code system.

    Attributes:
        language (Optional[str]): The language in which the designation is expressed.
        use (Optional[Coding]): The type of designation (e.g., synonym, preferred term).
        value (str): The actual text of the designation.
    """
    language: Optional[str] = None
    use: Optional[Coding] = None
    value: str

class CodeSystemConceptProperty(BaseModel):
    """
    Represents a property of a concept within a FHIR CodeSystem.

    Attributes:
        code (str): The property code that identifies the type of property.
        valueCode (Optional[str]): A coded value for the property, if applicable.
        valueCoding (Optional[Coding]): A Coding object representing the property value.
        valueString (Optional[str]): A string value for the property.
        valueInteger (Optional[int]): An integer value for the property.
        valueBoolean (Optional[bool]): A boolean value for the property.
        valueDateTime (Optional[str]): A date-time value for the property, represented as a string.
        valueDecimal (Optional[float]): A decimal value for the property.
    """
    code: str
    valueCode: Optional[str] = None
    valueCoding: Optional[Coding] = None
    valueString: Optional[str] = None
    valueInteger: Optional[int] = None
    valueBoolean: Optional[bool] = None
    valueDateTime: Optional[str] = None
    valueDecimal: Optional[float] = None

class CodeSystemConcept(BaseModel):
    """
    Represents a concept within a FHIR CodeSystem resource.

    Attributes:
        code (str): The code that identifies the concept.
        display (Optional[str]): A human-readable string for the concept.
        definition (Optional[str]): A formal definition of the concept.
        designation (Optional[List[CodeSystemConceptDesignation]]): Additional designations for the concept.
        property (Optional[List[CodeSystemConceptProperty]]): Properties associated with the concept.
        concept (Optional[List[Any]]): Nested concepts, allowing for recursive concept hierarchies.
    """
    code: str
    display: Optional[str] = None
    definition: Optional[str] = None
    designation: Optional[List[CodeSystemConceptDesignation]] = None
    property: Optional[List[CodeSystemConceptProperty]] = None
    concept: Optional[List[Any]] = None  # Nested concepts (recursive); use Any for simplicity

class CodeSystem(BaseModel):
    """
    Represents a FHIR CodeSystem resource.

    Attributes:
        resourceType (Literal["CodeSystem"]): The type of the resource (always "CodeSystem").
        id (Optional[str]): Logical id of the resource.
        url (Optional[str]): Canonical identifier for the code system.
        version (Optional[str]): Version of the code system.
        name (Optional[str]): Name for this code system.
        status (str): Status of the code system (e.g., "active", "draft").
        content (str): The content mode of the code system.
        experimental (Optional[bool]): If true, indicates the code system is experimental.
        date (Optional[str]): Date when the code system was published.
        publisher (Optional[str]): Name of the publisher.
        description (Optional[str]): Natural language description of the code system.
        caseSensitive (Optional[bool]): If true, code comparisons are case sensitive.
        valueSet (Optional[str]): Canonical reference to the value set.
        hierarchyMeaning (Optional[str]): The meaning of the hierarchy of concepts.
        compositional (Optional[bool]): If true, supports compositional grammar.
        versionNeeded (Optional[bool]): If true, indicates if the version is needed.
        count (Optional[int]): Total number of concepts defined.
        concept (Optional[List[CodeSystemConcept]]): List of concepts defined in the code system.
    """
    resourceType: Literal["CodeSystem"] = "CodeSystem"
    id: Optional[str] = None
    url: Optional[str] = None
    version: Optional[str] = None
    name: Optional[str] = None
    status: str
    content: str
    experimental: Optional[bool] = None
    date: Optional[str] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    caseSensitive: Optional[bool] = None
    valueSet: Optional[str] = None
    hierarchyMeaning: Optional[str] = None
    compositional: Optional[bool] = None
    versionNeeded: Optional[bool] = None
    count: Optional[int] = None
    concept: Optional[List[CodeSystemConcept]] = None

class ValueSetComposeIncludeConceptDesignation(BaseModel):
    """
    Represents a designation for a concept within a ValueSet compose include.

    Attributes:
        language (Optional[str]): The language in which the designation is expressed.
        use (Optional[Any]): The coding that specifies the use or purpose of the designation.
        value (str): The text value of the designation.
    """
    language: Optional[str] = None
    use: Optional[Any] = None  # Could be a Coding, use Any for simplicity
    value: str

class ValueSetComposeIncludeConcept(BaseModel):
    """
    Represents a concept to be included in a FHIR ValueSet compose include.

    Attributes:
        code (str): The code identifying the concept.
        display (Optional[str]): A human-readable representation of the concept.
        designation (Optional[List[ValueSetComposeIncludeConceptDesignation]]): Additional designations for the concept, such as language-specific names.
    """
    code: str
    display: Optional[str] = None
    designation: Optional[List[ValueSetComposeIncludeConceptDesignation]] = None

class ValueSetComposeIncludeFilter(BaseModel):
    """
    Represents a filter for including concepts in a FHIR ValueSet compose element.

    Attributes:
        property (str): The property to filter on (e.g., code, system, display).
        op (str): The operation to apply for filtering (e.g., '=', 'in', 'exists').
        value (str): The value to compare against the property.
    """
    property: str
    op: str
    value: str

class ValueSetComposeInclude(BaseModel):
    """
    Represents the 'include' element of a FHIR ValueSet compose definition.

    Attributes:
        system (Optional[str]): The URI of the code system from which codes are included.
        version (Optional[str]): The version of the code system to use.
        concept (Optional[List[ValueSetComposeIncludeConcept]]): Specific concepts to be included from the code system.
        filter (Optional[List[ValueSetComposeIncludeFilter]]): Filters to select codes to be included.
        valueSet (Optional[List[str]]): References to other value sets whose codes should be included.
    """
    system: Optional[str] = None
    version: Optional[str] = None
    concept: Optional[List[ValueSetComposeIncludeConcept]] = None
    filter: Optional[List[ValueSetComposeIncludeFilter]] = None
    valueSet: Optional[List[str]] = None

class ValueSetCompose(BaseModel):
    """
    Represents the 'compose' element of a FHIR ValueSet resource.

    Attributes:
        lockedDate (Optional[str]): The date that the composition was locked. No further changes to the content are permitted after this date.
        inactive (Optional[bool]): If true, indicates that inactive concepts are included in the ValueSet.
        include (List[ValueSetComposeInclude]): A list of criteria for concepts or codes to be included in the ValueSet.
        exclude (Optional[List[ValueSetComposeInclude]]): A list of criteria for concepts or codes to be excluded from the ValueSet.
    """
    lockedDate: Optional[str] = None
    inactive: Optional[bool] = None
    include: List[ValueSetComposeInclude]
    exclude: Optional[List[ValueSetComposeInclude]] = None

class ValueSetExpansionParameter(BaseModel):
    """
    Represents a parameter used in the expansion of a FHIR ValueSet.

    Attributes:
        name (str): The name of the parameter.
        valueString (Optional[str]): The string value of the parameter, if applicable.
        valueBoolean (Optional[bool]): The boolean value of the parameter, if applicable.
        valueInteger (Optional[int]): The integer value of the parameter, if applicable.
        valueDecimal (Optional[float]): The decimal value of the parameter, if applicable.
        valueUri (Optional[str]): The URI value of the parameter, if applicable.
        valueCode (Optional[str]): The code value of the parameter, if applicable.
    """
    name: str
    valueString: Optional[str] = None
    valueBoolean: Optional[bool] = None
    valueInteger: Optional[int] = None
    valueDecimal: Optional[float] = None
    valueUri: Optional[str] = None
    valueCode: Optional[str] = None

class ValueSetExpansionContains(BaseModel):
    """
    Represents an element within a FHIR ValueSet expansion's 'contains' array.

    Attributes:
        system (Optional[str]): The system URI that defines the code.
        abstract (Optional[bool]): Indicates if the code is abstract (not selectable).
        inactive (Optional[bool]): Indicates if the code is inactive.
        version (Optional[str]): The version of the code system.
        code (Optional[str]): The code value.
        display (Optional[str]): The human-readable display for the code.
        contains (Optional[List[Any]]): Nested list of further contained codes (recursive structure).
    """
    system: Optional[str] = None
    abstract: Optional[bool] = None
    inactive: Optional[bool] = None
    version: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None
    contains: Optional[List[Any]] = None  # Recursive

class ValueSetExpansion(BaseModel):
    """
    Represents the expansion of a FHIR ValueSet, including metadata and the expanded concepts.

    Attributes:
        identifier (Optional[str]): Unique identifier for the expansion instance.
        timestamp (Optional[str]): Timestamp when the expansion was generated.
        total (Optional[int]): Total number of concepts in the expansion.
        offset (Optional[int]): Offset for paging through the expansion results.
        parameter (Optional[List[ValueSetExpansionParameter]]): Parameters used during the expansion.
        contains (Optional[List[ValueSetExpansionContains]]): List of concepts included in the expansion.
    """
    identifier: Optional[str] = None
    timestamp: Optional[str] = None
    total: Optional[int] = None
    offset: Optional[int] = None
    parameter: Optional[List[ValueSetExpansionParameter]] = None
    contains: Optional[List[ValueSetExpansionContains]] = None

class ValueSet(BaseModel):
    """
    Represents a FHIR ValueSet resource.

    Attributes:
        resourceType (Literal["ValueSet"]): The type of the resource, always "ValueSet".
        id (Optional[str]): Logical id of the resource.
        url (Optional[str]): Canonical identifier for the ValueSet.
        version (Optional[str]): Business version of the ValueSet.
        name (Optional[str]): Name for this ValueSet (computer friendly).
        status (Optional[str]): Status of the ValueSet (e.g., draft, active, retired).
        experimental (Optional[bool]): Indicates if the ValueSet is experimental.
        date (Optional[str]): Date when the ValueSet was published.
        publisher (Optional[str]): Name of the publisher.
        description (Optional[str]): Natural language description of the ValueSet.
        immutable (Optional[bool]): Indicates if the ValueSet is immutable.
        compose (Optional[ValueSetCompose]): Criteria for selecting codes for the ValueSet.
        expansion (Optional[ValueSetExpansion]): Expansion of the ValueSet for use.
    """
    resourceType: Literal["ValueSet"] = "ValueSet"
    id: Optional[str] = None
    url: Optional[str] = None
    version: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    experimental: Optional[bool] = None
    date: Optional[str] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    immutable: Optional[bool] = None
    compose: Optional[ValueSetCompose] = None
    expansion: Optional[ValueSetExpansion] = None