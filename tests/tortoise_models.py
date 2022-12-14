import enum
import tortoise


class ProductSource(enum.Enum):
    WAREHOUSE = "warehouse"
    SHOP = "shop"


class ProductCategory(tortoise.Model):
    id = tortoise.fields.IntField(pk=True)
    name = tortoise.fields.CharField(63)
    description = tortoise.fields.CharField(255)

    class Meta:
        table: str = "product_categories"


class Product(tortoise.Model):
    id = tortoise.fields.IntField(pk=True)
    category: tortoise.fields.ForeignKeyRelation[
        "ProductCategory"
    ] = tortoise.fields.ForeignKeyField("models.ProductCategory")
    name = tortoise.fields.CharField(255)
    is_active = tortoise.fields.BooleanField(default=True)
    source = tortoise.fields.CharEnumField(ProductSource)

    class Meta:
        table: str = "products"
