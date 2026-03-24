"""
用户模型
对应建表语句中的 users 表
"""

from sqlalchemy import Column, String, DateTime, JSON, Text
from sqlalchemy.sql import func

try:
    from backend.app.core.database import Base
except ImportError:
    from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True, comment="用户ID")
    school_id = Column(String(50), nullable=False, comment="学校ID，多租户隔离")
    grade = Column(String(20), nullable=False, comment="年级，如大一/2024级")
    major = Column(String(100), nullable=False, comment="专业")
    phone_number = Column(String(20), unique=True, comment="手机号")
    user_name = Column(String(100), nullable=False, comment="用户名")
    role = Column(String(20), nullable=False, comment="角色：teacher/student")
    contact_info = Column(JSON, comment="联系信息，JSON格式")
    profile_text = Column(Text, comment="用户补充说明（学习基础、目标等）")
    profile_ext = Column(JSON, comment="结构化画像扩展（兴趣、偏好交互模式等）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, name={self.user_name}, role={self.role})>"
