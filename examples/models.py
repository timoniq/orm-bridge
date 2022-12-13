from ormar import Model, ModelMeta, Integer, String


class User(Model):
    class Meta(ModelMeta):
        tablename: str = "users"
        abstract = True

    id = Integer(primary_key=True, autoincrement=True, nullable=False)
    name = String(max_length=31, nullable=False, default="Anonymous")
