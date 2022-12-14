import ormar

from orm_bridge.bridge.ormar import OrmarBridge
from orm_bridge.mapping import FieldType


class User(ormar.Model):
    id = ormar.Integer(primary_key=True, autoincrement=True, nullable=False)
    name = ormar.String(max_length=31, nullable=False, default="Anonymous")
    is_active = ormar.Boolean(default=True)

    class Meta(ormar.ModelMeta):
        tablename: str = "users"
        abstract = True


def test_ormar_mapping():
    bridge = OrmarBridge()
    mapping = bridge.get_mapping(User)
    assert len(mapping.fields) == 3
    assert mapping.name == "user"
    assert mapping.fields[0].type == FieldType.INTEGER
    assert mapping.fields[0].name == "id"
    assert mapping.fields[1].type == FieldType.STRING
    assert mapping.fields[1].name == "name"
    assert mapping.fields[2].type == FieldType.BOOLEAN
    assert mapping.fields[2].name == "is_active"
    assert mapping.fields[2].default is True
