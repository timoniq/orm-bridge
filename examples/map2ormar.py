import orm_bridge
from orm_bridge.bridge.ormar import OrmarBridge

mapping = orm_bridge.ModelMapping(
    name="users",
    fields=[
        orm_bridge.FieldMapping(
            type=orm_bridge.FieldType.INTEGER,
            name="id",
            primary_key=True,
        ),
        orm_bridge.FieldMapping(
            type=orm_bridge.FieldType.STRING,
            name="name",
        )
    ]
)

ormar_bridge = OrmarBridge()
ormar_model = ormar_bridge.get_model(mapping)

print(ormar_model)
