"""
数据库连接模块
配置 SQLAlchemy 引擎和 Session
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

try:
    from backend.app.core.config import settings
except ImportError:
    from app.core.config import settings

logger = logging.getLogger(__name__)

def _build_database_url() -> str:
    db_config = settings.DB_CONFIG
    target_db = settings.TARGET_DB
    protocol = "postgresql+asyncpg" if not db_config.get("ssl") else "postgresql+asyncpg"
    return f"{protocol}://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{target_db}"

DATABASE_URL = _build_database_url()
DATABASE_URL_SYNC = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

db_config = settings.DB_CONFIG
timeout = db_config.get("timeout", 5)

engine = create_engine(
    DATABASE_URL_SYNC,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    connect_args={
        "connect_timeout": timeout,
        "options": "-c statement_timeout={}000".format(timeout)
    },
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    try:
        from backend.app.models import (
            User,
            CourseCategory,
            Course,
            Lesson,
            CIRSection,
            QARecord,
            LearningProgress,
            Subject,
            Chapter,
            NewCourse,
            Slide,
            CourseDocument,
            LessonPlan,
            PPT
        )
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def check_db_connection() -> bool:
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def get_pool_status() -> dict:
    return {
        "pool_size": engine.pool.size(),
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "invalid": engine.pool.invalidatedcount() if hasattr(engine.pool, 'invalidatedcount') else 0
    }
