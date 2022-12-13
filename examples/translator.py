from orm_bridge import Translator
from .models import User

from orm_bridge.bridge.ormar import OrmarBridge
from orm_bridge.bridge.tortoise import TortoiseBridge

translator = Translator(OrmarBridge(), TortoiseBridge())

tortoise_model = translator.translate(User)
print(tortoise_model)
