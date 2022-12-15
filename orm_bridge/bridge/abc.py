import abc
import enum
import typing

from orm_bridge.mapping import FieldMapping, FieldType, ModelMapping
from orm_bridge.environment import Environment

Model = typing.TypeVar("Model")
ORMField = typing.TypeVar("ORMField")


class ErrorMode(enum.IntEnum):
    IGNORE = enum.auto()
    PANIC = enum.auto()


class FieldBridge(abc.ABC, typing.Generic[ORMField]):
    """Base class for field bridges"""

    def __init__(self, model_bridge: "Bridge") -> None:
        self.model_bridge = model_bridge

    @abc.abstractmethod
    def mapping_to_field(self, mapping: FieldMapping) -> ORMField:
        pass

    @abc.abstractmethod
    def field_to_mapping(self, name: str, field: ORMField) -> FieldMapping:
        pass


class Bridge(abc.ABC, typing.Generic[Model]):
    """Base class for bridges"""

    fields: dict[FieldType, typing.Type[FieldBridge]]

    def __init__(
        self,
        environment: typing.Optional[Environment[Model]] = None,
        field_error: ErrorMode = ErrorMode.PANIC,
        **kwargs,
    ) -> None:
        self.field_error = field_error
        self.environment: Environment = environment or Environment()
        self.kwargs = kwargs

    @abc.abstractmethod
    def get_model(self, mapping: ModelMapping) -> typing.Type[Model]:
        pass

    @abc.abstractmethod
    def get_mapping(self, model: typing.Type[Model]) -> ModelMapping:
        pass

    @abc.abstractmethod
    def get_tablename(self, model: typing.Type[Model]) -> str:
        pass

    @classmethod
    def field(
        cls,
        field_type: FieldType,
    ) -> typing.Callable[[typing.Type[FieldBridge]], typing.Type[FieldBridge]]:
        """Decorator to wrap ORM-specific field bridges"""

        def wrapper(bridge_cls: typing.Type[FieldBridge]) -> typing.Type[FieldBridge]:
            cls.fields[field_type] = bridge_cls
            return bridge_cls

        return wrapper
