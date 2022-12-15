import typing

from orm_bridge.bridge import Bridge
from orm_bridge.errors import BridgeError
from orm_bridge.environment import Environment

FromModel = typing.TypeVar("FromModel")
ToModel = typing.TypeVar("ToModel")


class TranslationResult(typing.Generic[FromModel, ToModel]):
    def __init__(
        self, translations: list[tuple[typing.Type[FromModel], typing.Type[ToModel]]]
    ) -> None:
        self.translations = translations

    def __getitem__(self, model: typing.Type[FromModel]) -> typing.Type[ToModel]:  # type: ignore
        for old_model, translation in self.translations:
            if old_model.__name__ == model.__name__:
                return translation
        raise BridgeError(f"Model `{model}` is not found in translated models")

    def __contains__(self, model: typing.Type[FromModel]) -> bool:
        for old_model, _ in self.translations:
            if old_model.__name__ == model.__name__:
                return True
        return False


class Translator:
    """Translates model from one ORM to another"""

    def __init__(self, from_orm: Bridge[FromModel], to_orm: Bridge[ToModel]) -> None:
        self.from_orm = from_orm
        self.to_orm = to_orm

    def translate(
        self,
        model: typing.Type[FromModel],
        name: typing.Optional[str] = None,
    ) -> typing.Type[ToModel]:
        """Translates single model"""

        mapping = self.from_orm.get_mapping(model)
        new_model = self.to_orm.get_model(mapping)
        if name is not None:
            self.to_orm.environment.table_models[name] = new_model
            self.from_orm.environment.table_models[name] = model
        return new_model

    def translate_many(
        self,
        *models: typing.Type[FromModel],
        environment: typing.Optional[Environment] = None,
    ) -> TranslationResult[FromModel, ToModel]:
        """Translates multiple models in environment"""

        env = environment or Environment()
        self.from_orm.environment = env
        self.to_orm.environment = env

        result: TranslationResult[FromModel, ToModel] = TranslationResult([])

        for model in models:
            mapping = self.from_orm.get_mapping(model)
            if mapping.name in env.table_models:
                new_model = env.table_models[mapping.name]
            else:
                new_model = self.to_orm.get_model(mapping)
            result.translations.append((model, new_model))

        return result
