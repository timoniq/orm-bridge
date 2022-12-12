from .abc import Bridge, FieldBridge
from orm_bridge.mapping import ModelMapping, FieldMapping, FieldType

import ormar

class OrmarBridge(Bridge[ormar.BaseModel]):
    def get_model(self, mapping: ModelMapping) -> ormar.BaseModel:
        pass

    def get_mapping(self, model: ormar.BaseModel) -> ModelMapping:
        pass


@OrmarBridge.field(FieldType.INTEGER)
class IntegerOrmar(FieldBridge[ormar.fields.Integer]):

    def mapping_to_field(self, mapping: FieldMapping) -> ormar.fields.Integer:
        pass

    def field_to_mapping(self, field: ormar.fields.Integer) -> FieldMapping:
        pass
