import tortoise
import enum

from orm_bridge.bridge.tortoise import TortoiseBridge
from orm_bridge.mapping import FieldType, FieldMapping


class ProductSource(enum.Enum):
    WAREHOUSE = "warehouse"
    SHOP = "shop"


class Product(tortoise.Model):
    id = tortoise.fields.IntField(pk=True)
    name = tortoise.fields.CharField(255)
    is_active = tortoise.fields.BooleanField(default=True)
    source = tortoise.fields.CharEnumField(ProductSource)


def test_tortoise_mapping():
    bridge = TortoiseBridge()
    mapping = bridge.get_mapping(Product)
    assert mapping.name == "products"
    assert len(mapping.fields) == 4
    assert mapping.fields[0] == FieldMapping(
        name="id",
        type=FieldType.INTEGER,
        primary_key=True,
        index=True,
        unique=True,
    )
    assert mapping.fields[1] == FieldMapping(
        name="name",
        type=FieldType.STRING,
        max_length=255,
    )
    assert mapping.fields[2] == FieldMapping(
        name="is_active",
        type=FieldType.BOOLEAN,
        default=True,
    )
    assert mapping.fields[3] == FieldMapping(
        name="source",
        type=FieldType.STRING,
        max_length=9,
        choices={"warehouse", "shop"},
    )
