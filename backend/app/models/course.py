"""
课程模型 (Legacy)
对应 lessons, courses 表
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import json

try:
    from backend.app.core.database import Base
except ImportError:
    from app.core.database import Base


class CourseCategory(Base):
    """课程分类表"""
    __tablename__ = "course_categories"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("course_categories.id"), nullable=True)
    created_at = Column(DateTime, server_default="now()")


class Course(Base):
    """课程表 - 对应 courses 表"""
    __tablename__ = "courses"
    __table_args__ = {'extend_existing': True}

    course_id = Column(String(100), primary_key=True)
    school_id = Column(String(50), nullable=False)
    category_id = Column(Integer, ForeignKey("course_categories.id"))
    course_name = Column(String(500), nullable=False)
    teacher_id = Column(String(100))
    term = Column(String(50))
    ext_info = Column(Text)

    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    """课时表 - 对应 lessons 表"""
    __tablename__ = "lessons"
    __table_args__ = {'extend_existing': True}

    lesson_id = Column(String(100), primary_key=True)
    course_id = Column(String(100), ForeignKey("courses.course_id"), nullable=False)
    school_id = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    cover_image = Column(String(500))
    file_type = Column(String(50))
    file_url = Column(String(1000))
    category = Column(String(100))
    task_status = Column(String(50), default="pending")
    created_at = Column(DateTime, server_default="now()")
    completed_at = Column(DateTime)
    file_info = Column(JSON)
    mind_map = Column(JSON)

    cir_sections = relationship("CIRSection", back_populates="lesson", cascade="all, delete-orphan")
    course = relationship("Course", back_populates="lessons")

    @property
    def mind_map_data(self):
        if self.mind_map:
            if isinstance(self.mind_map, dict):
                return self.mind_map
            try:
                return json.loads(self.mind_map)
            except:
                pass
        return None

    @mind_map_data.setter
    def mind_map_data(self, value):
        self.mind_map = value if isinstance(value, dict) else (json.dumps(value, ensure_ascii=False) if value else None)
