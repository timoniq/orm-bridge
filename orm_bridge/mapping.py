import enum
import typing

import pydantic


Value = typing.Any


class FieldType(enum.Enum):
    INTEGER = "integer"
    STRING = "string"
    BOOLEAN = "boolean"


class FieldMapping(pydantic.BaseModel):
    type: FieldType
    name: str
    nullable: bool = False
    choices: typing.Optional[set[Value]] = None
    default: typing.Optional[Value] = None
    primary_key: bool = False
    max_length: int = 255
    ge: typing.Optional[int] = None
    le: typing.Optional[int] = None
    autoincrement: bool = False
    unique: bool = False
    index: bool = False


class ModelMapping(pydantic.BaseModel):
    name: str
    fields: list[FieldMapping]
