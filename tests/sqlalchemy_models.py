from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, SmallInteger

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(40))
    is_active = Column(Boolean, default=True)
    age = Column(SmallInteger, nullable=True)
