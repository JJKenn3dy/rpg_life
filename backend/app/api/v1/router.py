from fastapi import APIRouter

from .endpoints import users, domains

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
