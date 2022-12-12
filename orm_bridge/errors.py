from .mapping import FieldType

class BridgeError(Exception):
    pass


class MappingError(BridgeError):
    pass


class NoFieldBridge(BridgeError):
    def __init__(self, field_name: str, field_type: FieldType) -> None:
        self.field_name = field_name
        self.field_type = field_type
    
    def __str__(self) -> str:
        return (
            f"There is no field bridge for field `{self.field_name}` of type {self.field_type.value}"
        )
