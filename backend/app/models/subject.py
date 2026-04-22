"""
科目与章节模型
对应 subjects 和 chapters 表
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import relationship

try:
    from backend.app.core.database import Base
except ImportError:
    from app.core.database import Base


class Subject(Base):
    """科目表"""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="科目ID")
    name = Column(String(100), nullable=False, comment="科目名称")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # 关联关系
    chapters = relationship("Chapter", back_populates="subject", cascade="all, delete-orphan")
    courses = relationship("NewCourse", back_populates="subject")

    def __repr__(self):
        return f"<Subject(id={self.id}, name={self.name})>"


class Chapter(Base):
    """章节表"""
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="章节ID")
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, comment="所属科目ID")
    name = Column(String(100), nullable=False, comment="章节名称")
    order = Column(Integer, default=0, comment="章节顺序")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # 关联关系
    subject = relationship("Subject", back_populates="chapters")
    courses = relationship("NewCourse", back_populates="chapter")

    def __repr__(self):
        return f"<Chapter(id={self.id}, name={self.name}, subject_id={self.subject_id})>"
