from fastapi import APIRouter
from . import ws_script
from .endpoints import async_tts

router = APIRouter()
router.include_router(ws_script.router, tags=["script"])
router.include_router(async_tts.router)