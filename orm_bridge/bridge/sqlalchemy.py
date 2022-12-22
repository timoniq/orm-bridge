import typing

import sqlalchemy
from sqlalchemy.orm import declarative_base

from orm_bridge.errors import FieldBridgeError, NoFieldBridge
from orm_bridge.mapping import FieldMapping, FieldType, ModelMapping

from orm_bridge.bridge.abc import Bridge, FieldBridge, ErrorMode

SQLALCHEMY_TYPE_MAPPING = {
    "integer": FieldType.INTEGER,
    "small_integer": FieldType.INTEGER,
    "big_integer": FieldType.INTEGER,
    "float": FieldType.FLOAT,
    "string": FieldType.STRING,
    "boolean": FieldType.BOOLEAN,
}
Base = declarative_base()


class SQLAlchemyBridge(Bridge[sqlalchemy.Table]):
    fields = {}

    def get_model(self, mapping: ModelMapping) -> typing.Type[sqlalchemy.Table]:
        fields: dict = {}

        for field in mapping.fields:
            if field.type not in self.fields:
                raise NoFieldBridge(field.name, field.type)
            field_mapping = self.fields[field.type](self)
            fields[field.name] = field_mapping.mapping_to_field(field)

        params: dict[str, typing.Any] = {**fields, "__tablename__": mapping.name}
        return type(mapping.name, (Base,), params)  # type: ignore

    def get_mapping(self, model: typing.Type[sqlalchemy.Table]) -> ModelMapping:
        fields: list[FieldMapping] = []

        try:
            model_columns = model.__table__.columns
        except AttributeError:
            model_columns = model.columns

        for column in model_columns:
            field_type = column.type.__class__.__visit_name__
            mapped_field_type = SQLALCHEMY_TYPE_MAPPING.get(field_type)
            if not mapped_field_type:
                if self.field_error == ErrorMode.IGNORE:
                    continue
                raise FieldBridgeError(
                    column.name,
                    f"no translation for sqlalchemy field type {field_type}",
                )
            field_mapping = self.fields[mapped_field_type](self)
            fields.append(field_mapping.field_to_mapping(column.name, column))

        return ModelMapping(name=model.__tablename__, fields=fields)

    def get_tablename(self, model: typing.Type[sqlalchemy.Table]) -> str:
        return model.__tablename__


NumberField = typing.Union[sqlalchemy.Integer, sqlalchemy.Float]


@SQLAlchemyBridge.field(FieldType.INTEGER)
@SQLAlchemyBridge.field(FieldType.FLOAT)
class NumericSQLAlchemy(FieldBridge[sqlalchemy.INTEGER]):
    def mapping_to_field(self, mapping: FieldMapping) -> sqlalchemy.Column[NumberField]:
        field_type = (
            sqlalchemy.Integer
            if mapping.type == FieldType.INTEGER
            else FieldType.FLOAT
        )
        return sqlalchemy.Column(
            field_type,
            nullable=mapping.nullable,
            default=mapping.default,
            primary_key=mapping.primary_key,
            index=mapping.index,
        )

    def field_to_mapping(self, name: str, field: NumberField) -> FieldMapping:
        info = field.__dict__
        unique = info.get("unique", False)
        index = info.get("index", False)
        default = info.get("default")
        default = default.arg if default else None
        return FieldMapping(
            name=name,
            type=FieldType.INTEGER,
            nullable=info["nullable"],
            default=default,
            primary_key=info.get("primary_key", False),
            unique=unique if unique else False,
            index=index if index else False,
        )


@SQLAlchemyBridge.field(FieldType.STRING)
class StringSQLAlchemy(FieldBridge[sqlalchemy.String]):
    def mapping_to_field(self, mapping: FieldMapping) -> sqlalchemy.Column[sqlalchemy.String]:
        return sqlalchemy.Column(
            sqlalchemy.String(mapping.max_length),
            nullable=mapping.nullable,
            default=mapping.default,
            primary_key=mapping.primary_key,
            index=mapping.index,
        )

    def field_to_mapping(self, name: str, field: sqlalchemy.String) -> FieldMapping:
        info = field.__dict__
        unique = info.get("unique", False)
        index = info.get("index", False)
        default = info.get("default")
        default = default.arg if default else None
        return FieldMapping(
            name=name,
            type=FieldType.STRING,
            nullable=info["nullable"],
            max_length=info["type"].length,
            default=default,
            primary_key=info.get("primary_key", False),
            unique=unique if unique else False,
            index=index if index else False,
        )


@SQLAlchemyBridge.field(FieldType.BOOLEAN)
class BooleanSQLAlchemy(FieldBridge[sqlalchemy.Boolean]):
    def mapping_to_field(self, mapping: FieldMapping) -> sqlalchemy.Column[sqlalchemy.Boolean]:
        return sqlalchemy.Column(
            sqlalchemy.Boolean,
            nullable=mapping.nullable,
            default=mapping.default,
            primary_key=mapping.primary_key,
            index=mapping.index,
        )

    def field_to_mapping(self, name: str, field: sqlalchemy.Boolean) -> FieldMapping:
        info = field.__dict__
        unique = info.get("unique", False)
        index = info.get("index", False)
        default = info.get("default")
        default = default.arg if default else None
        return FieldMapping(
            name=name,
            type=FieldType.BOOLEAN,
            nullable=info["nullable"],
            default=default,
            primary_key=info.get("primary_key", False),
            unique=unique if unique else False,
            index=index if index else False,
        )
