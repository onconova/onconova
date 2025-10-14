from enum import Enum
from uuid import UUID as UuidType
from typing import Annotated, Generic, Optional, TypeVar, Any
from typing_extensions import TypeAliasType
from django.db.models import Model as DjangoModel
from pydantic import GetJsonSchemaHandler, GetCoreSchemaHandler, AfterValidator, WithJsonSchema
from pydantic_core import core_schema


class RemoveAnyOfNull:
    """
    A class for customizing Pydantic JSON schema generation by removing 'null' types from 'anyOf' schemas.
    """

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ):
        schema = handler(core_schema)
        # Remove "null" from anyOf
        if "anyOf" in schema:
            schema["anyOf"] = [s for s in schema["anyOf"] if s.get("type") != "null"]
            if len(schema["anyOf"]) == 1:
                schema.update(schema["anyOf"][0])
                schema.pop("anyOf", None)
        return schema


T = TypeVar("T")

#: A generic type alias for an optional value that removes 'null' from 'anyOf' in Pydantic JSON schema.
#: Use this to indicate a value may be None, but have cleaner generated schemas.
Nullable = Annotated[Optional[T], RemoveAnyOfNull()]


class UUID(UuidType):
    
    @classmethod
    def _validate(cls, v: UuidType | DjangoModel) -> UuidType:
        return getattr(v, 'id', None) if isinstance(v, DjangoModel) else v

    @classmethod
    def _serialize(cls, v: 'UUID') -> UuidType:
        return v

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_before_validator_function(
            cls._validate,
            core_schema.uuid_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.uuid_schema(),
            ),
        )



class Age(int):
    """
    A custom integer type representing an age value.

    This class can be used to provide semantic meaning to variables or parameters
    that specifically represent age, while retaining all behaviors of the built-in int type.
    """

    @classmethod
    def _validate(cls, v: int) -> 'Age':
        return cls(int(v))

    @classmethod
    def _serialize(cls, v: 'Age') -> int:
        return int(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.int_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.int_schema(),
            ),
        )



class Username(str):
    """
    A custom string type representing a username.

    This class is used to provide type distinction for usernames within the application,
    while retaining all behaviors of the built-in `str` type.
    """

    @classmethod
    def _validate(cls, v: str) -> 'Username':
        return cls(str(v))

    @classmethod
    def _serialize(cls, v: 'Username') -> str:
        return str(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )



class Contributors(list, Generic[T]):
    """
    A list of usernames
    """

    @classmethod
    def _serialize(cls, v: T) -> T:
        return v

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._serialize,
            core_schema.list_schema(core_schema.str_schema()),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.list_schema(core_schema.str_schema()),
            ),
        )



class AgeBin(str, Enum):
    """
    Enumeration representing age bins as string values.

    Each member corresponds to a specific age range, with the following options:

    - SUB_20: "<20"         (under 20 years old)
    - AGE_20_24: "20-24"    (20 to 24 years old)
    - AGE_25_29: "25-29"    (25 to 29 years old)
    - AGE_30_34: "30-34"    (30 to 34 years old)
    - AGE_35_39: "35-39"    (35 to 39 years old)
    - AGE_40_44: "40-44"    (40 to 44 years old)
    - AGE_45_49: "45-49"    (45 to 49 years old)
    - AGE_50_54: "50-56"    (50 to 54 years old)
    - AGE_55_59: "55-59"    (55 to 59 years old)
    - AGE_60_64: "60-64"    (60 to 64 years old)
    - AGE_65_69: "65-69"    (65 to 69 years old)
    - AGE_70_74: "70-74"    (70 to 74 years old)
    - AGE_75_79: "75-79"    (75 to 79 years old)
    - AGE_80_84: "80-84"    (80 to 84 years old)
    - AGE_85_89: "85-89"    (85 to 89 years old)
    - OVER_90: "90+"        (90 years old and above)

    The string value of each member is returned when the member is converted to a string.
    """

    SUB_20 = "<20"
    AGE_20_24 = "20-24"
    AGE_25_29 = "25-29"
    AGE_30_34 = "30-34"
    AGE_35_39 = "35-39"
    AGE_40_44 = "40-44"
    AGE_45_49 = "45-49"
    AGE_50_54 = "50-56"
    AGE_55_59 = "55-59"
    AGE_60_64 = "60-64"
    AGE_65_69 = "65-69"
    AGE_70_74 = "70-74"
    AGE_75_79 = "75-79"
    AGE_80_84 = "80-84"
    AGE_85_89 = "85-89"
    OVER_90 = "90+"

    def __str__(self):
        return self.value
