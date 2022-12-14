import ormar

from orm_bridge.bridge.ormar import OrmarBridge
from orm_bridge.mapping import FieldType, FieldMapping


class User(ormar.Model):
    id = ormar.Integer(primary_key=True, autoincrement=True, nullable=False)
    name = ormar.String(max_length=31, nullable=False, default="Anonymous")
    is_active = ormar.Boolean(default=True, nullable=False)
    role = ormar.String(max_length=31, choices=["customer", "seller"], nullable=False)

    class Meta(ormar.ModelMeta):
        tablename: str = "users"
        abstract = True


def test_ormar_mapping():
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
