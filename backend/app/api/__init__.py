"""
API package
"""
from app.api.tournaments import router as tournaments_router

__all__ = [
    "tournaments_router",
]