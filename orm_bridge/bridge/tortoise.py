import typing

import tortoise

from orm_bridge.errors import FieldBridgeError, NoFieldBridge
from orm_bridge.mapping import FieldMapping, FieldType, ModelMapping

from orm_bridge.bridge.abc import Bridge, FieldBridge

TORTOISE_TYPE_MAPPING = {
    "IntField": FieldType.INTEGER,
    "CharField": FieldType.STRING,
}


class TortoiseBridge(Bridge[tortoise.Model]):

    fields = {}

    def get_model(self, mapping: ModelMapping) -> typing.Type[tortoise.Model]:
        fields: dict[str, tortoise.fields.Field] = {}

        for field in mapping.fields:
            if field.type not in self.fields:
                raise NoFieldBridge(field.name, field.type)
            field_mapping = self.fields[field.type]()
            fields[field.name] = field_mapping.mapping_to_field(field)

        params: dict[str, typing.Any] = {**fields}
        return type(mapping.name, (tortoise.Model,), params)  # type: ignore

    def get_mapping(self, model: typing.Type[tortoise.Model]) -> ModelMapping:
        fields: list[FieldMapping] = []

        for name, field in model._meta.fields_map.items():
            field_type = TORTOISE_TYPE_MAPPING.get(field.__class__.__name__)
            if not field_type:
                raise FieldBridgeError(
                    name,
                    f"no translation for ormar type {field.__class__.__name__}",
                )
            field_mapping = self.fields[field_type]()
            fields.append(field_mapping.field_to_mapping(name, field))

        return ModelMapping(name="", fields=fields)


@TortoiseBridge.field(FieldType.INTEGER)
class IntegerTortoise(FieldBridge[tortoise.fields.IntField]):

    def mapping_to_field(self, mapping: FieldMapping) -> tortoise.fields.IntField:
        validators: list[tortoise.validators.Validator] = []

        if mapping.ge is not None:
            validators.append(tortoise.validators.MinValueValidator(mapping.ge))
        if mapping.le is not None:
            validators.append(tortoise.validators.MaxValueValidator(mapping.le))

        return tortoise.fields.IntField(
            pk=mapping.primary_key,
            unique=mapping.unique,
            null=mapping.nullable,
            default=mapping.default,
            validators=validators,
            index=mapping.index,
        )

    def field_to_mapping(self, name: str, field: tortoise.fields.IntField) -> FieldMapping:
        kwargs: dict[str, int] = {}
        field_info: dict = field.__dict__

        for validator in field_info.get("validators", []):
            if isinstance(validator, tortoise.validators.MinValueValidator):
                kwargs["ge"] = int(validator.min_value)
            elif isinstance(validator, tortoise.validators.MaxValueValidator):
                kwargs["le"] = int(validator.max_value)

        return FieldMapping(
            name=name,
            type=FieldType.INTEGER,
            nullable=field_info["null"],
            primary_key=field_info["pk"],
            unique=field_info["unique"],
            default=field_info["default"],
            index=field_info["index"],
            **kwargs,
        )


@TortoiseBridge.field(FieldType.STRING)
class StringTortoise(FieldBridge[tortoise.fields.CharField]):
    def mapping_to_field(self, mapping: FieldMapping) -> tortoise.fields.CharField:
        return tortoise.fields.CharField(
            mapping.max_length,
            null=mapping.nullable,
            pk=mapping.primary_key,
            default=mapping.default,
            unique=mapping.unique,
            index=mapping.index,
        )

    def field_to_mapping(self, name: str, field: tortoise.fields.CharField) -> FieldMapping:
        field_info: dict = field.__dict__
        return FieldMapping(
            name=name,
            type=FieldType.STRING,
            nullable=field_info["null"],
            primary_key=field_info["pk"],
            max_length=field_info["max_length"],
            unique=field_info["unique"],
            default=field_info["default"],
            index=field_info["index"],
        )


@TortoiseBridge.field(FieldType.BOOLEAN)
class BooleanTortoise(FieldBridge[tortoise.fields.BooleanField]):
    def mapping_to_field(self, mapping: FieldMapping) -> tortoise.fields.BooleanField:
        return tortoise.fields.BooleanField(
            null=mapping.nullable,
            default=mapping.default,
            index=mapping.index,
        )

    def field_to_mapping(
            self,
            name: str,
            field: tortoise.fields.BooleanField,
    ) -> FieldMapping:
        field_info: dict = field.__dict__
        return FieldMapping(
            name=name,
            type=FieldType.BOOLEAN,
            nullable=field_info["null"],
            default=field_info["default"],
            index=field_info["index"],
        )
