import typing
import enum

import tortoise

from orm_bridge.errors import FieldBridgeError, NoFieldBridge
from orm_bridge.mapping import FieldMapping, FieldType, ModelMapping

from orm_bridge.bridge.abc import Bridge, FieldBridge, ErrorMode

TORTOISE_TYPE_MAPPING = {
    "IntField": FieldType.INTEGER,
    "CharField": FieldType.STRING,
    "CharEnumFieldInstance": FieldType.STRING,
    "BooleanField": FieldType.BOOLEAN,
    "ForeignKeyFieldInstance": FieldType.FOREIGN_KEY,
}


def get_tablename(model: typing.Type[tortoise.Model]) -> str:
    return model._meta.db_table or model.__name__.lower() + "s"


def get_tortoise_name(tablename: str, bridge: Bridge) -> str:
    if (
        "tortoise_names" in bridge.environment.options
        and tablename in bridge.environment.options["tortoise_names"].values()
    ):
        tortoise_names: dict[str, str] = bridge.environment.options["tortoise_names"]
        return list(tortoise_names.keys())[
            list(tortoise_names.values()).index(tablename)
        ]

    # Guessing the tortoise name
    if tablename.endswith("ies"):
        tablename = tablename.removesuffix("ies") + "y"
    elif tablename.endswith("es"):
        tablename = tablename.removesuffix("es")
    else:
        tablename = tablename.removesuffix("s")
    return "models." + tablename.capitalize()


class TortoiseBridge(Bridge[tortoise.Model]):

    fields = {}

    def get_model(self, mapping: ModelMapping) -> typing.Type[tortoise.Model]:
        fields: dict[str, tortoise.fields.Field] = {}

        for field in mapping.fields:
            if field.type not in self.fields:
                raise NoFieldBridge(field.name, field.type)
            field_mapping = self.fields[field.type](self)
            fields[field.name] = field_mapping.mapping_to_field(field)

        params: dict[str, typing.Any] = {**fields}

        class Meta:
            table: str = mapping.name

        params["Meta"] = Meta
        return type(
            get_tortoise_name(mapping.name, self),
            (tortoise.Model,),
            params
        )

    def get_mapping(self, model: typing.Type[tortoise.Model]) -> ModelMapping:
        fields: list[FieldMapping] = []

        for name, field in model._meta.fields_map.items():
            field_type = TORTOISE_TYPE_MAPPING.get(field.__class__.__name__)
            if not field_type:
                if self.field_error == ErrorMode.IGNORE:
                    continue
                raise FieldBridgeError(
                    name,
                    f"no translation for ormar type {field.__class__.__name__}",
                )
            field_mapping = self.fields[field_type](self)
            fields.append(field_mapping.field_to_mapping(name, field))

        return ModelMapping(name=get_tablename(model), fields=fields)

    def get_tablename(self, model: typing.Type[tortoise.Model]) -> str:
        return get_tablename(model)


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

    def field_to_mapping(
        self, name: str, field: tortoise.fields.IntField
    ) -> FieldMapping:
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
        fields = dict(
            null=mapping.nullable,
            pk=mapping.primary_key,
            default=mapping.default,
            unique=mapping.unique,
            index=mapping.index,
        )
        if mapping.choices:
            choices = enum.Enum("Choices", {c.upper(): c for c in mapping.choices})  # type: ignore
            return tortoise.fields.CharEnumField(  # type: ignore
                enum_type=choices, **fields  # type: ignore
            )
        return tortoise.fields.CharField(
            mapping.max_length,
            **fields,
        )

    def field_to_mapping(
        self, name: str, field: tortoise.fields.CharField
    ) -> FieldMapping:
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
            choices=(
                self.convert_choice_enum(field_info["enum_type"])
                if field_info.get("enum_type")
                else None
            ),
        )

    @classmethod
    def convert_choice_enum(cls, choice_enum: typing.Type[enum.Enum]) -> set[str]:
        return set(element.value for element in choice_enum)


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


@TortoiseBridge.field(FieldType.FOREIGN_KEY)
class FKTortoise(FieldBridge[tortoise.fields.ForeignKeyRelation]):
    def mapping_to_field(
        self, mapping: FieldMapping
    ) -> tortoise.fields.ForeignKeyRelation:
        assert mapping.tablename is not None

        tortoise_name: str = get_tortoise_name(mapping.tablename, self.model_bridge)
        return tortoise.fields.ForeignKeyField(
            tortoise_name,
        )

    def field_to_mapping(
        self,
        name: str,
        field: tortoise.fields.ForeignKeyRelation,
    ) -> FieldMapping:
        info = field.__dict__

        tablename: str = ""

        if "tortoise_names" in self.model_bridge.environment.options:
            tablename = self.model_bridge.environment.options["tortoise_names"].get(
                info["model_name"]
            )
        if not tablename:
            # Guessing the tablename
            tablename = info["model_name"].split(".")[-1].lower() + "s"

        return FieldMapping(
            name=name,
            type=FieldType.FOREIGN_KEY,
            tablename=tablename,
        )
