from examples.models import User
from orm_bridge.bridge.ormar import OrmarBridge

bridge = OrmarBridge()
mapping = bridge.get_mapping(User)

print(mapping)
