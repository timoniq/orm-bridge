import abc
import typing
from orm_bridge.mapping import ModelMapping, FieldMapping, FieldType
from orm_bridge.field import Field

Model = typing.TypeVar("Model")
ORMField = typing.TypeVar("ORMField")
FieldConverter = typing.Callable[[Field], ORMField]


class FieldBridge(abc.ABC, typing.Generic[ORMField]):
    """Base class for field bridges"""

    @abc.abstractmethod
    def mapping_to_field(self, mapping: FieldMapping) -> ORMField:
        pass

    @abc.abstractmethod
    def field_to_mapping(self, field: ORMField) -> FieldMapping:
        pass


class Bridge(abc.ABC, typing.Generic[Model]):
    """Base class for bridges"""

    fields: dict[FieldType, typing.Type[FieldBridge]] = {}
    
    @abc.abstractmethod
    def get_model(self, mapping: ModelMapping) -> typing.Type[Model]:
        pass

    @abc.abstractmethod
    def get_mapping(self, model: typing.Type[Model]) -> ModelMapping:
        pass

    @classmethod
    def field(
        cls, 
        field_type: FieldType,
    ) -> typing.Callable[[typing.Type[FieldBridge]], typing.Type[FieldBridge]]:
        """Decorator to wrap ORM-specific field bridges"""

        def wrapper(
            bridge_cls: typing.Type[FieldBridge]
        ) -> typing.Type[FieldBridge]:
            cls.fields[field_type] = bridge_cls
            return bridge_cls
        
        return wrapper
