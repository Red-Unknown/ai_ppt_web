"""
课程模型（新）
对应 courses 表
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, func
from sqlalchemy.orm import relationship

try:
    from backend.app.core.database import Base
except ImportError:
    from app.core.database import Base


class NewCourse(Base):
    """课程表"""
    __tablename__ = "courses_new"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="课程ID")
    title = Column(String(200), nullable=False, comment="课程标题")
    description = Column(Text, comment="课程描述")
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="SET NULL"), comment="所属科目ID")
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"), comment="所属章节ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # 关联关系
    subject = relationship("Subject", back_populates="courses")
    chapter = relationship("Chapter", back_populates="courses")
    slides = relationship("Slide", back_populates="course", cascade="all, delete-orphan")
    documents = relationship("CourseDocument", back_populates="course", cascade="all, delete-orphan")
    lesson_plans = relationship("LessonPlan", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NewCourse(id={self.id}, title={self.title})>"


class Slide(Base):
    """幻灯片表"""
    __tablename__ = "slides"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="幻灯片ID")
    course_id = Column(Integer, ForeignKey("courses_new.id", ondelete="CASCADE"), nullable=False, comment="所属课程ID")
    slide_index = Column(Integer, nullable=False, comment="幻灯片顺序")
    image_url = Column(String(500), comment="图片URL")
    duration = Column(Integer, default=0, comment="显示时长(秒)")
    content = Column(Text, comment="幻灯片内容")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关联关系
    course = relationship("NewCourse", back_populates="slides")

    def __repr__(self):
        return f"<Slide(id={self.id}, course_id={self.course_id}, index={self.slide_index})>"


class CourseDocument(Base):
    """课程文档表"""
    __tablename__ = "course_documents"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="文档ID")
    course_id = Column(Integer, ForeignKey("courses_new.id", ondelete="CASCADE"), nullable=False, comment="所属课程ID")
    title = Column(String(200), nullable=False, comment="文档标题")
    content = Column(Text, comment="文档内容")
    doc_type = Column(String(50), default="text", comment="文档类型")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # 关联关系
    course = relationship("NewCourse", back_populates="documents")

    def __repr__(self):
        return f"<CourseDocument(id={self.id}, title={self.title})>"


class LessonPlan(Base):
    """教案表"""
    __tablename__ = "lesson_plans"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="教案ID")
    course_id = Column(Integer, ForeignKey("courses_new.id", ondelete="CASCADE"), nullable=False, comment="所属课程ID")
    content = Column(Text, nullable=False, comment="教案内容(JSON格式)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # 关联关系
    course = relationship("NewCourse", back_populates="lesson_plans")

    def __repr__(self):
        return f"<LessonPlan(id={self.id}, course_id={self.course_id})>"
