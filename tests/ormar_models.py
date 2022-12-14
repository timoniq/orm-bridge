import ormar


class User(ormar.Model):
    id = ormar.Integer(primary_key=True, autoincrement=True, nullable=False)
    name = ormar.String(max_length=31, nullable=False, default="Anonymous")
    is_active = ormar.Boolean(default=True, nullable=False)
    role = ormar.String(max_length=31, choices=["customer", "seller"], nullable=False)

    class Meta(ormar.ModelMeta):
        tablename: str = "users"
        pkname: str = "id"
        abstract = True


class Event(ormar.Model):
    id = ormar.Integer(primary_key=True, autoincrement=True, nullable=False)
    name = ormar.String(max_length=63)

    class Meta(ormar.ModelMeta):
        tablename: str = "events"
        pkname: str = "id"
        abstract = True


class Registration(ormar.Model):
    id = ormar.Integer(primary_key=True, autoincrement=True, nullable=False)
    user = ormar.ForeignKey(User)
    event = ormar.ForeignKey(Event)

    class Meta(ormar.ModelMeta):
        tablename: str = "registrations"
        abstract = True
