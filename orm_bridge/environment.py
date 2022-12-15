import typing
from orm_bridge.mapping import ModelMapping

Model = typing.TypeVar("Model")

TableModels = dict[str, typing.Type[Model]]
TableMappings = dict[str, ModelMapping]


class Environment(typing.Generic[Model]):
    def __init__(
        self,
        table_mappings: typing.Optional[TableMappings] = None,
        table_models: typing.Optional[TableModels] = None,
        **options,
    ):
        self.table_models: TableModels = table_models or {}
        self.table_mappings: TableMappings = table_mappings or {}
        self.options = options
