"""FastAPI APIRouters for Kelana AI Backend"""
from .auth import router as auth_router
from .chat import router as chat_router
from .recommendations import router as recommendations_router
from .trips import router as trips_router

__all__ = ["auth_router", "chat_router", "recommendations_router", "trips_router"]
