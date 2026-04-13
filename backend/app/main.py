import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import check_db_connection
from app.api.v1.endpoints.script import router as script_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI互动智课系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(script_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "API running"}

@app.on_event("startup")
def startup_event():
    logger.info("开始...")
    if check_db_connection():
        logger.info("数据库连接成功")
    else:
        logger.warning("数据库连接失败")
