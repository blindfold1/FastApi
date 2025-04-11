from .author import auth_router
from .clients import clients_router
from .foods import food_router


__all__ = ["auth_router", "clients_router", "food_router", "tracker_router"]

from .tracker import tracker_router
