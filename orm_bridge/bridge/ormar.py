from .abc import Bridge, FieldBridge

from orm_bridge.mapping import ModelMapping, FieldMapping, FieldType
from orm_bridge.errors import NoFieldBridge, FieldBridgeError, BridgeError

import ormar
import pydantic
import typing


ORMAR_TYPE_MAPPING = {
    "Integer": FieldType.INTEGER,
    "String": FieldType.STRING,
}


class OrmarBridge(Bridge[ormar.Model]):

    fields = {}

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
        meta: typing.Optional[ormar.ModelMeta] = getattr(model, "Meta", None)
        if not meta:
            raise BridgeError("Ormar model should have Meta")
        
        fields: list[FieldMapping] = []
        for name, model_field in meta.model_fields.items():
            field_type = ORMAR_TYPE_MAPPING.get(model_field.__class__.__name__)
            if not field_type:
                raise FieldBridgeError(name, f"no translation for ormar type {model_field.__class__.__name__}")
            field_mapping = self.fields[field_type]()
            fields.append(field_mapping.field_to_mapping(name, model_field))
        
        return ModelMapping(name=model.get_name(), fields=fields)


@OrmarBridge.field(FieldType.INTEGER)
class IntegerOrmar(FieldBridge[ormar.fields.Integer]):

    def mapping_to_field(self, mapping: FieldMapping) -> ormar.fields.Integer:
        return ormar.fields.Integer(
            nullable=mapping.nullable, 
            default=mapping.default,
            pk=mapping.primary_key,
            minimum=mapping.ge,  # type: ignore
            maximum=mapping.le,  # type: ignore
            autoincrement=mapping.autoincrement,
        )

    def field_to_mapping(self, name: str, field: ormar.fields.Integer) -> FieldMapping:
        info = field.__dict__
        return FieldMapping(
            name=name,
            type=FieldType.INTEGER,
            nullable=info["nullable"] and not info.get("primary_key"),
            default=info.get("default", None),
            primary_key=info.get("primary_key", False),
            ge=info.get("ge"),
            le=info.get("le"),
            unique=info["unique"],
        )


@OrmarBridge.field(FieldType.STRING)
class StringOrmar(FieldBridge[ormar.fields.String]):
    def mapping_to_field(self, mapping: FieldMapping) -> ormar.fields.String:
        return ormar.fields.String(
            nullable=mapping.nullable,
            default=mapping.default,
            primary_key=mapping.primary_key,
            max_length=mapping.max_length,
        )
    
    def field_to_mapping(self, name: str, field: ormar.fields.String) -> FieldMapping:
        info = field.__dict__
        return FieldMapping(
            name=name,
            type=FieldType.STRING,
            nullable=info["nullable"],
            default=info.get("default", None),
            primary_key=info.get("primary_key", False),
            unique=info["unique"],
        )
