from .abc import Bridge, FieldBridge

from orm_bridge.mapping import ModelMapping, FieldMapping, FieldType
from orm_bridge.errors import NoFieldBridge

import ormar
import typing

class OrmarBridge(Bridge[ormar.Model]):

    def get_model(self, mapping: ModelMapping) -> typing.Type[ormar.Model]:
        fields: dict[str, ormar.BaseField] = {}

        for field in mapping.fields:
            if field.type not in self.fields:
                raise NoFieldBridge(field.name, field.type)
            field_mapping = self.fields[field.type]()
            fields[field.name] = field_mapping.mapping_to_field(field)

        params: dict[str, typing.Any] = {**fields}
        return type(mapping.name, (ormar.Model,), params)  # type: ignore
    
    def get_mapping(self, model: typing.Type[ormar.Model]) -> ModelMapping:
        pass


@OrmarBridge.field(FieldType.INTEGER)
class IntegerOrmar(FieldBridge[ormar.fields.Integer]):

    def mapping_to_field(self, mapping: FieldMapping) -> ormar.fields.Integer:
        return ormar.fields.Integer(
            nullable=mapping.nullable, 
            default=mapping.default,
            pk=mapping.primary_key,
            minimum=mapping.minimum,  # type: ignore
            maximum=mapping.maximum,  # type: ignore
        )

    def field_to_mapping(self, field: ormar.fields.Integer) -> FieldMapping:
        pass


@OrmarBridge.field(FieldType.STRING)
class StringOrmar(FieldBridge[ormar.fields.String]):
    def mapping_to_field(self, mapping: FieldMapping) -> ormar.fields.String:
        return ormar.fields.String(
            nullable=mapping.nullable,
            default=mapping.default,
            pk=mapping.primary_key,
            max_length=mapping.max_length,
        )
    
    def field_to_mapping(self, field: ormar.fields.String) -> FieldMapping:
        pass
