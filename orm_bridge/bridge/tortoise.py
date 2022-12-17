import typing
import enum

import tortoise

from orm_bridge.errors import FieldBridgeError, NoFieldBridge
from orm_bridge.mapping import FieldMapping, FieldType, ModelMapping

from orm_bridge.bridge.abc import Bridge, FieldBridge, ErrorMode

TORTOISE_TYPE_MAPPING = {
    "IntField": FieldType.INTEGER,
    "BigIntField": FieldType.INTEGER,  # todo: add field types for these
    "SmallIntField": FieldType.INTEGER,
    "FloatField": FieldType.FLOAT,
    "CharField": FieldType.STRING,
    "CharEnumFieldInstance": FieldType.STRING,
    "BooleanField": FieldType.BOOLEAN,
    "ForeignKeyFieldInstance": FieldType.FOREIGN_KEY,
    "ManyToManyFieldInstance": FieldType.MANY2MANY,
}


def get_tablename(model: typing.Type[tortoise.Model]) -> str:
    return model._meta.db_table or model.__name__.lower() + "s"


def get_tablename_from_tortoise_name(tortoise_name: str, bridge: Bridge) -> str:
    tablename: str = ""

    if "tortoise_names" in bridge.environment.options:
        tablename = bridge.environment.options["tortoise_names"].get(tortoise_name)
    if not tablename:
        # Guessing the tablename
        tablename = tortoise_name.split(".")[-1].lower() + "s"
    return tablename


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
    elif tablename.endswith("sses"):
        tablename = tablename.removesuffix("es")
    else:
        tablename = tablename.removesuffix("s")
    return tablename.capitalize()


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
        return type(get_tortoise_name(mapping.name, self), (tortoise.Model,), params)

    def get_mapping(self, model: typing.Type[tortoise.Model]) -> ModelMapping:
        fields: list[FieldMapping] = []

        for name, field in model._meta.fields_map.items():
            field_type = TORTOISE_TYPE_MAPPING.get(field.__class__.__name__)
            if not field_type:
                if self.field_error == ErrorMode.IGNORE:
                    continue
                raise FieldBridgeError(
                    name,
                    f"no translation for tortoise type {field.__class__.__name__}",
                )
            field_mapping = self.fields[field_type](self)
            fields.append(field_mapping.field_to_mapping(name, field))

        return ModelMapping(name=get_tablename(model), fields=fields)

    def get_tablename(self, model: typing.Type[tortoise.Model]) -> str:
        return get_tablename(model)


NumberField = typing.Union[tortoise.fields.IntField, tortoise.fields.FloatField]


class NumberTortoise(FieldBridge[NumberField]):
    def mapping_to_field(self, mapping: FieldMapping) -> NumberField:
        validators: list[tortoise.validators.Validator] = []

        if mapping.ge is not None:
            validators.append(tortoise.validators.MinValueValidator(mapping.ge))
        if mapping.le is not None:
            validators.append(tortoise.validators.MaxValueValidator(mapping.le))

        field_t = (
            tortoise.fields.IntField
            if mapping.type == FieldType.INTEGER
            else tortoise.fields.FloatField
        )

        return field_t(
            pk=mapping.primary_key,
            unique=mapping.unique,
            null=mapping.nullable,
            default=mapping.default,
            validators=validators,
            index=mapping.index,
        )

    def field_to_mapping_with_type(
        self,
        name: str,
        field_type: FieldType,
        field: NumberField,
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
            type=field_type,
            nullable=field_info["null"],
            primary_key=field_info["pk"],
            unique=field_info["unique"],
            default=field_info["default"],
            index=field_info["index"],
            **kwargs,
        )

    def field_to_mapping(self, name: str, field: NumberField) -> FieldMapping:
        raise NotImplementedError()


@TortoiseBridge.field(FieldType.INTEGER)
class IntegerTortoise(NumberTortoise):
    def field_to_mapping(self, name: str, field: NumberField) -> FieldMapping:
        return self.field_to_mapping_with_type(name, FieldType.INTEGER, field)


@TortoiseBridge.field(FieldType.FLOAT)
class FloatTortoise(NumberTortoise):
    def field_to_mapping(self, name: str, field: NumberField) -> FieldMapping:
        return self.field_to_mapping_with_type(name, FieldType.FLOAT, field)


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
            choices = enum.Enum("Choices", {c: c for c in mapping.choices})  # type: ignore
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
            "models." + tortoise_name,
            source_field=mapping.name,
            related_name=mapping.related_name if not mapping.skip_reverse else False,
        )

    def field_to_mapping(
        self,
        name: str,
        field: tortoise.fields.ForeignKeyRelation,
    ) -> FieldMapping:
        info = field.__dict__

        return FieldMapping(
            name=name,
            type=FieldType.FOREIGN_KEY,
            tablename=get_tablename_from_tortoise_name(
                info["model_name"], self.model_bridge
            ),
            related_name=info["related_name"] or None,
            skip_reverse=info["related_name"] is False,
        )


@TortoiseBridge.field(FieldType.MANY2MANY)
class M2MTortoise(FieldBridge[tortoise.fields.ManyToManyRelation]):
    def mapping_to_field(
        self, mapping: FieldMapping
    ) -> tortoise.fields.ManyToManyRelation:
        assert mapping.tablename
        tortoise_name: str = get_tortoise_name(mapping.tablename, self.model_bridge)
        return tortoise.fields.ManyToManyField(
            "models." + tortoise_name,
            through=("models." + get_tortoise_name(mapping.through, self.model_bridge))
            if mapping.through
            else None,
        )

    def field_to_mapping(
        self, name: str, field: tortoise.fields.ManyToManyRelation
    ) -> FieldMapping:
        info = field.__dict__
        tablename = get_tablename_from_tortoise_name(
            info["model_name"], self.model_bridge
        )
        return FieldMapping(
            name=name,
            type=FieldType.MANY2MANY,
            tablename=tablename,
        )
