from fastapi import APIRouter
from . import ws_script

router = APIRouter()
router.include_router(ws_script.router, tags=["script"])