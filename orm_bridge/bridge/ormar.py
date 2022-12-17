import typing

import ormar

from orm_bridge.errors import BridgeError, FieldBridgeError, NoFieldBridge
from orm_bridge.mapping import FieldMapping, FieldType, ModelMapping

from orm_bridge.bridge.abc import Bridge, FieldBridge, ErrorMode

ORMAR_TYPE_MAPPING = {
    "Integer": FieldType.INTEGER,
    "SmallInteger": FieldType.INTEGER,  # todo: add field types for these
    "BigInteger": FieldType.INTEGER,
    "Float": FieldType.FLOAT,
    "String": FieldType.STRING,
    "Boolean": FieldType.BOOLEAN,
    "ForeignKey": FieldType.FOREIGN_KEY,
    "ManyToMany": FieldType.MANY2MANY,
}


class OrmarBridge(Bridge[ormar.Model]):

    fields = {}

    def get_model(self, mapping: ModelMapping) -> typing.Type[ormar.Model]:
        fields: dict[str, ormar.BaseField] = {}

        for field in mapping.fields:
            if field.type not in self.fields:
                raise NoFieldBridge(field.name, field.type)
            field_mapping = self.fields[field.type](self)
            fields[field.name] = field_mapping.mapping_to_field(field)

        params: dict[str, typing.Any] = {**fields}
        return type(mapping.name, (ormar.Model,), params)  # type: ignore

    def get_mapping(self, model: typing.Type[ormar.Model]) -> ModelMapping:
        meta: typing.Optional[ormar.ModelMeta] = getattr(model, "Meta", None)
        if not meta:
            raise BridgeError("Ormar model should have Meta")

        fields: list[FieldMapping] = []
        for name, model_field in meta.model_fields.items():
            field_info = model_field.__dict__
            if field_info["skip_field"] or field_info["virtual"]:
                continue
            field_type = ORMAR_TYPE_MAPPING.get(model_field.__class__.__name__)
            if not field_type:
                if self.field_error == ErrorMode.IGNORE:
                    continue
                raise FieldBridgeError(
                    name,
                    f"no translation for ormar type {model_field.__class__.__name__}",
                )
            field_mapping = self.fields[field_type](self)
            fields.append(field_mapping.field_to_mapping(name, model_field))

        return ModelMapping(name=meta.tablename, fields=fields)

    def get_tablename(self, model: typing.Type[ormar.Model]) -> str:
        meta: typing.Optional[ormar.ModelMeta] = getattr(model, "Meta", None)
        if not meta:
            raise BridgeError("Ormar model should have Meta")
        return meta.tablename


NumberField = typing.Union[ormar.fields.Integer, ormar.fields.Float]


@OrmarBridge.field(FieldType.INTEGER)
@OrmarBridge.field(FieldType.FLOAT)
class NumberOrmar(FieldBridge[NumberField]):
    def mapping_to_field(self, mapping: FieldMapping) -> NumberField:
        field_t = (
            ormar.fields.Integer
            if mapping.type == FieldType.INTEGER
            else FieldType.FLOAT
        )
        return field_t(
            nullable=mapping.nullable,
            default=mapping.default,
            pk=mapping.primary_key,
            minimum=mapping.ge,  # type: ignore
            maximum=mapping.le,  # type: ignore
            autoincrement=mapping.autoincrement,
            index=mapping.index,
        )

    def field_to_mapping(self, name: str, field: NumberField) -> FieldMapping:
        info = field.__dict__
        return FieldMapping(
            name=name,
            type=FieldType.INTEGER if info["__type__"] == int else FieldType.FLOAT,
            nullable=info["nullable"] and not info.get("primary_key"),
            default=info.get("ormar_default", None),
            primary_key=info.get("primary_key", False),
            ge=info.get("ge"),
            le=info.get("le"),
            unique=info["unique"],
            index=info.get("index", False),
        )


@OrmarBridge.field(FieldType.STRING)
class StringOrmar(FieldBridge[ormar.fields.String]):
    def mapping_to_field(self, mapping: FieldMapping) -> ormar.fields.String:
        return ormar.fields.String(
            nullable=mapping.nullable,
            default=mapping.default,
            primary_key=mapping.primary_key,
            max_length=mapping.max_length,
            index=mapping.index,
            choices=mapping.choices,
        )

    def field_to_mapping(self, name: str, field: ormar.fields.String) -> FieldMapping:
        info = field.__dict__
        return FieldMapping(
            name=name,
            type=FieldType.STRING,
            nullable=info["nullable"],
            max_length=info["column_type"].length,
            default=info.get("ormar_default", None),
            primary_key=info.get("primary_key", False),
            unique=info["unique"],
            index=info.get("index", False),
            choices=info.get("choices") or None,
        )


@OrmarBridge.field(FieldType.BOOLEAN)
class BooleanOrmar(FieldBridge[ormar.fields.model_fields.BaseField]):
    def mapping_to_field(
        self, mapping: FieldMapping
    ) -> ormar.fields.model_fields.BaseField:
        return ormar.fields.Boolean(  # type: ignore
            nullable=mapping.nullable,
            default=mapping.default,
            index=mapping.index,
        )

    def field_to_mapping(
        self,
        name: str,
        field: ormar.fields.model_fields.BaseField,
    ) -> FieldMapping:
        info = field.__dict__
        return FieldMapping(
            name=name,
            type=FieldType.BOOLEAN,
            nullable=info["nullable"],
            default=info.get("ormar_default", None),
            index=info.get("index", False),
        )


@OrmarBridge.field(FieldType.FOREIGN_KEY)
class FKOrmar(FieldBridge[ormar.fields.ForeignKeyField]):
    def mapping_to_field(self, mapping: FieldMapping) -> ormar.fields.ForeignKeyField:
        raise NotImplementedError()

    def field_to_mapping(
        self,
        name: str,
        field: ormar.fields.ForeignKeyField,
    ) -> FieldMapping:
        info = field.__dict__

        fk_constraint = info["constraints"][0]
        tablename = fk_constraint.reference.split(".", 1)[0]

        return FieldMapping(
            name=name,
            type=FieldType.FOREIGN_KEY,
            index=info.get("index", False),
            tablename=tablename,
            related_name=info["related_name"],
            skip_reverse=info["skip_reverse"],
        )


@OrmarBridge.field(FieldType.MANY2MANY)
class M2MOrmar(FieldBridge[ormar.fields.ManyToManyField]):
    def mapping_to_field(self, mapping: FieldMapping) -> ormar.fields.ManyToManyField:
        raise NotImplementedError()

    def field_to_mapping(
        self, name: str, field: ormar.fields.ManyToManyField
    ) -> FieldMapping:
        info = field.__dict__
        to_model = info["to"]
        return FieldMapping(
            name=name,
            type=FieldType.MANY2MANY,
            tablename=self.model_bridge.get_tablename(to_model),
            through=info["through_relation_name"],
        )
