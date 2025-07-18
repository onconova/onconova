from enum import Enum
from typing import Annotated, Optional, TypeVar

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema


class RemoveAnyOfNull:
    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ):
        schema = handler(core_schema)
        # Remove "null" from anyOf
        if "anyOf" in schema:
            schema["anyOf"] = [s for s in schema["anyOf"] if s.get("type") != "null"]
            if len(schema["anyOf"]) == 1:
                schema.update(schema["anyOf"][0])
                schema.pop("anyOf")
        return schema


T = TypeVar("T")
Nullable = Annotated[Optional[T], RemoveAnyOfNull()]


class Age(int):
    pass


class Username(str):
    pass


class Array(list):
    pass


class AgeBin(str, Enum):
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
