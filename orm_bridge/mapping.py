import pydantic
import typing
import enum

AnyValue = typing.Union[int, float, str]

class FieldType(enum.Enum):
    INTEGER = "integer"
    STRING = "string"


class FieldMapping(pydantic.BaseModel):
    type: FieldType
    name: str
    nullable: bool = False
    default: typing.Optional[AnyValue] = None
    primary_key: bool = False
    max_length: int = 255
    minimum: typing.Optional[int] = None
    maximum: typing.Optional[int] = None

class ModelMapping(pydantic.BaseModel):
    name: str
    fields: list[FieldMapping]
