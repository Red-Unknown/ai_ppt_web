from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    # 使用 user_name 作为主键，匹配数据库表结构
    user_name = Column(String(50), primary_key=True, unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # student 或 teacher
    name = Column(String(50), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    student_id = Column(String(50), unique=True, nullable=True)
    teacher_id = Column(String(50), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库
def init_db():
    try:
        # 使用原始SQL删除表，处理级联关系
        from sqlalchemy import text
        with engine.connect() as conn:
            # 先删除依赖表
            conn.execute(text("DROP TABLE IF EXISTS courses CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS qa_records CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS learning_progress CASCADE"))
            # 再删除users表
            conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            conn.commit()
        # 重新创建表
        Base.metadata.create_all(bind=engine)
        print("数据库表初始化成功")
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
