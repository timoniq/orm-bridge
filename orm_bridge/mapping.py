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

class ModelMapping(pydantic.BaseModel):
    fields: list[FieldMapping]
