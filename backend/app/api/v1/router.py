from fastapi import APIRouter

from .endpoints import users, domains
from . import daily_logs

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(daily_logs.router, prefix="/daily-logs", tags=["daily_logs"])
