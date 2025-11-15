"""
API package
"""
from app.api.tournaments import router as tournaments_router
from app.api.matches import router as matches_router

__all__ = [
    "tournaments_router",
    "matches_router",
]