from orm_bridge.bridge.ormar import OrmarBridge
from orm_bridge.bridge.tortoise import TortoiseBridge
from orm_bridge.translator import Translator
from orm_bridge.mapping import FieldMapping, FieldType

from tests.ormar_models import User, Event, Registration, Promocode


def test_translator() -> None:
    translator = Translator(OrmarBridge(), TortoiseBridge())
    result = translator.translate_many(User, Event, Registration, Promocode)
    assert User in result
    assert Event in result
    assert Registration in result
    user = result[User]
    assert user.__module__ == "tortoise.models"
    mapping = TortoiseBridge().get_mapping(user)
    assert mapping.name == "users"
    assert len(mapping.fields) == 4
    assert mapping.fields[0] == FieldMapping(
        name="id",
        type=FieldType.INTEGER,
        primary_key=True,
        nullable=False,
        unique=True,
        index=True,
    )
    assert mapping.fields[1] == FieldMapping(
        name="name",
        type=FieldType.STRING,
        max_length=31,
        nullable=False,
        default="Anonymous",
    )
    assert mapping.fields[2] == FieldMapping(
        name="is_active",
        type=FieldType.BOOLEAN,
        default=True,
    )
    assert mapping.fields[3] == FieldMapping(
        name="role",
        type=FieldType.STRING,
        max_length=8,
        choices={"customer", "seller"},
    )

    promocode = result[Promocode]
    mapping = TortoiseBridge().get_mapping(promocode)
    assert mapping.fields[2] == FieldMapping(
        name="events",
        type=FieldType.MANY2MANY,
        tablename="events",
    )
