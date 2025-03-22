"""
Router registry.

This module imports and exports all API routers for easy inclusion in the main application.
"""

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.style_profiles import router as style_profiles_router
from app.routers.images import router as images_router
from app.routers.recommendations import router as recommendations_router

routers = [
    auth_router,
    users_router,
    style_profiles_router,
    images_router,
    recommendations_router,
] 