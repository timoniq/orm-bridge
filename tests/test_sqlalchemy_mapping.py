import orm_bridge
from orm_bridge.bridge.sqlalchemy import SQLAlchemyBridge
from orm_bridge.mapping import FieldType, FieldMapping
from tests.sqlalchemy_models import User


def test_sqlalchemy_mapping() -> None:
    bridge = SQLAlchemyBridge()
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
        name="username",
        type=FieldType.STRING,
        nullable=True,
        max_length=40,
    )
    assert mapping.fields[2] == FieldMapping(
        name="is_active",
        type=FieldType.BOOLEAN,
        default=True,
        nullable=True,
    )
    assert mapping.fields[3] == FieldMapping(
        name="age",
        type=FieldType.INTEGER,
        nullable=True,
    )


def test_mapping_to_sqlalchemy():
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
            ),
            orm_bridge.FieldMapping(
                type=orm_bridge.FieldType.STRING,
                max_length=301,
                name="description",
            ),
        ],
    )
    bridge = SQLAlchemyBridge()
    model = bridge.get_model(mapping)

    assert model.__tablename__ == "users"
    assert len(model.__table__.columns) == 3
    assert model.__table__.columns[0].name == "id"
    assert model.__table__.columns[1].name == "name"
    assert model.__table__.columns[2].name == "description"
    assert model.__table__.columns[0].type.__class__.__visit_name__ == FieldType.INTEGER.value
    assert model.__table__.columns[1].type.__class__.__visit_name__ == FieldType.STRING.value
    assert model.__table__.columns[2].type.__class__.__visit_name__ == FieldType.STRING.value
    assert model.__table__.columns[2].__dict__["type"].length == 301
