import tortoise

from orm_bridge.bridge.tortoise import TortoiseBridge
from orm_bridge.mapping import FieldType


class Product(tortoise.Model):
    id = tortoise.fields.IntField(pk=True)
    name = tortoise.fields.CharField(255)


def test_tortoise_mapping():
    bridge = TortoiseBridge()
    mapping = bridge.get_mapping(Product)
    assert mapping.fields[0].type == FieldType.INTEGER
    assert mapping.fields[0].name == "id"
    assert mapping.fields[1].type == FieldType.STRING
    assert mapping.fields[1].name == "name"
