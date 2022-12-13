from .bridge import Bridge
import typing
import enum

FromModel = typing.TypeVar("FromModel")
ToModel = typing.TypeVar("ToModel")


class Translator:
    """Translates model from one ORM to another"""
    
    def __init__(
        self, 
        from_orm: Bridge[FromModel], 
        to_orm: Bridge[ToModel]
    ) -> None:
        self.from_orm = from_orm
        self.to_orm = to_orm
    
    def translate(self, model: typing.Type[FromModel]) -> typing.Type[ToModel]:
        mapping = self.from_orm.get_mapping(model)
        return self.to_orm.get_model(mapping)
