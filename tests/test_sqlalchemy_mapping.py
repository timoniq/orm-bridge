from orm_bridge.bridge.sqlalchemy import SQLAlchemyBridge
from orm_bridge.mapping import FieldType, FieldMapping
from tests.sqlalchemy_models import User


def test_sqlalchemy_mapping() -> None:
    bridge = SQLAlchemyBridge()
    mapping = bridge.get_mapping(User)
    assert mapping.name == "users"
    assert len(mapping.fields) == 4
    assert mapping.fields[0] == FieldMapping(
        name="id",
        type=FieldType.INTEGER,
        primary_key=True,
        nullable=False,
    )
    assert mapping.fields[1] == FieldMapping(
        name="username",
        type=FieldType.STRING,
        nullable=True,
        max_length=40,
    )
    assert mapping.fields[2] == FieldMapping(
        name="is_active",
        type=FieldType.BOOLEAN,
        default=True,
        nullable=True,
    )
    assert mapping.fields[3] == FieldMapping(
        name="age",
        type=FieldType.INTEGER,
        nullable=True,
    )
