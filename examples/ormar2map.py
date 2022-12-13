from orm_bridge.bridge.ormar import OrmarBridge
from .models import User

bridge = OrmarBridge()
mapping = bridge.get_mapping(User)

print(mapping)
