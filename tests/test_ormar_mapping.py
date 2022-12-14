from orm_bridge.bridge.ormar import OrmarBridge
from orm_bridge.mapping import FieldType, FieldMapping
from tests.ormar_models import User, Registration


def test_ormar_mapping() -> None:
    bridge = OrmarBridge()
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
        max_length=31,
        choices={"customer", "seller"},
    )


def test_ormar_mapping_fk() -> None:
    bridge = OrmarBridge()
    mapping = bridge.get_mapping(Registration)
    assert mapping.fields[0] == FieldMapping(
        name="id",
        type=FieldType.INTEGER,
        primary_key=True,
        nullable=False,
    )
    assert mapping.fields[1] == FieldMapping(
        name="user",
        type=FieldType.FOREIGN_KEY,
        tablename="users",
    )
