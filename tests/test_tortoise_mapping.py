from orm_bridge.bridge.tortoise import TortoiseBridge
from orm_bridge.mapping import FieldType, FieldMapping

from tests.tortoise_models import Product, ProductCategory


def test_tortoise_mapping() -> None:
    bridge = TortoiseBridge(
        model_names={
            "models.ProductCategory": ProductCategory,
            "models.Product": Product,
        }
    )
    mapping = bridge.get_mapping(Product)
    assert mapping.name == "products"
    assert len(mapping.fields) == 5
    assert mapping.fields[0] == FieldMapping(
        name="id",
        type=FieldType.INTEGER,
        primary_key=True,
        index=True,
        unique=True,
    )
    assert mapping.fields[1] == FieldMapping(
        name="category",
        type=FieldType.FOREIGN_KEY,
        tablename="product_categories",
    )
    assert mapping.fields[2] == FieldMapping(
        name="name",
        type=FieldType.STRING,
        max_length=255,
    )
    assert mapping.fields[3] == FieldMapping(
        name="is_active",
        type=FieldType.BOOLEAN,
        default=True,
    )
    assert mapping.fields[4] == FieldMapping(
        name="source",
        type=FieldType.STRING,
        max_length=9,
        choices={"warehouse", "shop"},
    )
