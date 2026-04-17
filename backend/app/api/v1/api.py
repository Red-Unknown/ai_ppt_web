from fastapi import APIRouter
from app.api.v1.endpoints import script
from app.api.v1.endpoints import retrieval
from app.api.v1.endpoints import subjects
from app.api.v1.endpoints import courses
from app.api.v1.endpoints import ppts

api_router = APIRouter()
api_router.include_router(script.router)
api_router.include_router(retrieval.router)
api_router.include_router(subjects.router)
api_router.include_router(subjects.chapter_router)
api_router.include_router(courses.router)
api_router.include_router(ppts.router)
