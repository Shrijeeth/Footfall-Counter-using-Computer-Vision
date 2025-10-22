from fastapi import APIRouter

from app.api.v1.endpoints import auth, configurations, processing, users, websocket

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    configurations.router, prefix="/configurations", tags=["configurations"]
)
api_router.include_router(processing.router, prefix="/processing", tags=["processing"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
