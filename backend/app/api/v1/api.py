from fastapi import APIRouter
from app.api.v1.endpoints import script

api_router = APIRouter()
api_router.include_router(script.router)