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

# 创建同步引擎（使用 psycopg2）
# 将 asyncpg URL 转换为 psycopg2 URL
DATABASE_URL_SYNC = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(
    DATABASE_URL_SYNC,
    pool_pre_ping=True,  # 自动检测断开的连接
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG  # 调试模式下打印 SQL
)

# 创建 SessionLocal 类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 Base 类，用于 ORM Model 继承
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    依赖注入函数，用于 FastAPI 的 Depends
    使用方式: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    初始化数据库，创建所有表
    注意：生产环境建议使用 Alembic 迁移
    """
    try:
        # 导入所有模型以确保它们被注册到 Base.metadata
        from backend.app.models import (
            User,
            CourseCategory,
            Course,
            Lesson,
            CIRSection,
            QARecord,
            LearningProgress
        )
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def check_db_connection() -> bool:
    """
    检查数据库连接是否正常
    Returns:
        bool: 连接成功返回 True，否则返回 False
    """
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
