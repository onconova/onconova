from typing import List, Optional, Any, Literal
from pydantic import BaseModel, Field, RootModel

class Coding(BaseModel):
    system: Optional[str] = None
    version: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None
    userSelected: Optional[bool] = None

class CodeSystemConceptDesignation(BaseModel):
    language: Optional[str] = None
    use: Optional[Coding] = None
    value: str

class CodeSystemConceptProperty(BaseModel):
    code: str
    valueCode: Optional[str] = None
    valueCoding: Optional[Coding] = None
    valueString: Optional[str] = None
    valueInteger: Optional[int] = None
    valueBoolean: Optional[bool] = None
    valueDateTime: Optional[str] = None
    valueDecimal: Optional[float] = None

class CodeSystemConcept(BaseModel):
    code: str
    display: Optional[str] = None
    definition: Optional[str] = None
    designation: Optional[List[CodeSystemConceptDesignation]] = None
    property: Optional[List[CodeSystemConceptProperty]] = None
    concept: Optional[List[Any]] = None  # Nested concepts (recursive); use Any for simplicity

class CodeSystem(BaseModel):
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
    language: Optional[str] = None
    use: Optional[Any] = None  # Could be a Coding, use Any for simplicity
    value: str

class ValueSetComposeIncludeConcept(BaseModel):
    code: str
    display: Optional[str] = None
    designation: Optional[List[ValueSetComposeIncludeConceptDesignation]] = None

class ValueSetComposeIncludeFilter(BaseModel):
    property: str
    op: str
    value: str

class ValueSetComposeInclude(BaseModel):
    system: Optional[str] = None
    version: Optional[str] = None
    concept: Optional[List[ValueSetComposeIncludeConcept]] = None
    filter: Optional[List[ValueSetComposeIncludeFilter]] = None
    valueSet: Optional[List[str]] = None

class ValueSetCompose(BaseModel):
    lockedDate: Optional[str] = None
    inactive: Optional[bool] = None
    include: List[ValueSetComposeInclude]
    exclude: Optional[List[ValueSetComposeInclude]] = None

class ValueSetExpansionParameter(BaseModel):
    name: str
    valueString: Optional[str] = None
    valueBoolean: Optional[bool] = None
    valueInteger: Optional[int] = None
    valueDecimal: Optional[float] = None
    valueUri: Optional[str] = None
    valueCode: Optional[str] = None

class ValueSetExpansionContains(BaseModel):
    system: Optional[str] = None
    abstract: Optional[bool] = None
    inactive: Optional[bool] = None
    version: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None
    contains: Optional[List[Any]] = None  # Recursive

class ValueSetExpansion(BaseModel):
    identifier: Optional[str] = None
    timestamp: Optional[str] = None
    total: Optional[int] = None
    offset: Optional[int] = None
    parameter: Optional[List[ValueSetExpansionParameter]] = None
    contains: Optional[List[ValueSetExpansionContains]] = None

class ValueSet(BaseModel):
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