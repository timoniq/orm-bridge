import ormar

class User(ormar.Model):
    class Meta(ormar.ModelMeta):
        tablename: str = "users"
        abstract = True

    id = ormar.Integer(primary_key=True, autoincrement=True, nullable=False)
    name = ormar.String(max_length=31, nullable=False, default="Anonymous")


import tortoise


class Product(tortoise.Model):
    id = tortoise.fields.IntField(pk=True)
    name = tortoise.fields.CharField(255)
    in_stock = tortoise.fields.IntField()
