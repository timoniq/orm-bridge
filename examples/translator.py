from orm_bridge import Translator
from orm_bridge.bridge.ormar import OrmarBridge
from orm_bridge.bridge.tortoise import TortoiseBridge

from examples.models import User

translator = Translator(OrmarBridge(), TortoiseBridge())

tortoise_model = translator.translate(User)
print(tortoise_model)
