from fastapi import APIRouter
from app.api.v1.endpoints import script
from app.api.v1.endpoints import retrieval

api_router = APIRouter()
api_router.include_router(script.router)
api_router.include_router(retrieval.router)