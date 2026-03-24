"""
课程相关模型
对应建表语句中的 course_categories, courses, lessons 表
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

try:
    from backend.app.core.database import Base
except ImportError:
    from app.core.database import Base


class CourseCategory(Base):
    """课程分类表"""
    __tablename__ = "course_categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    school_id = Column(String(50), nullable=False, comment="学校ID，隔离")
    category_name = Column(String(100), nullable=False, comment="分类名称")
    sort_order = Column(Integer, default=0, comment="排序")

    # 关系
    courses = relationship("Course", back_populates="category")

    def __repr__(self):
        return f"<CourseCategory(id={self.category_id}, name={self.category_name})>"


class Course(Base):
    """课程体系表"""
    __tablename__ = "courses"

    course_id = Column(String(50), primary_key=True, comment="课程ID")
    school_id = Column(String(50), nullable=False, comment="学校ID，隔离")
    category_id = Column(Integer, ForeignKey("course_categories.category_id"), comment="分类ID")
    course_name = Column(String(200), nullable=False, comment="课程名称")
    teacher_id = Column(String(50), ForeignKey("users.user_id"), comment="教师ID")
    term = Column(String(20), comment="学期")
    ext_info = Column(JSON, comment="扩展信息")

    # 关系
    category = relationship("CourseCategory", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course")

    def __repr__(self):
        return f"<Course(id={self.course_id}, name={self.course_name})>"


class Lesson(Base):
    """课件任务表"""
    __tablename__ = "lessons"

    lesson_id = Column(String(50), primary_key=True, comment="课件ID，对应parseId")
    course_id = Column(String(50), ForeignKey("courses.course_id"), comment="课程ID")
    school_id = Column(String(50), nullable=False, comment="学校ID，隔离")
    title = Column(String(200), nullable=False, comment="标题")
    cover_image = Column(String(500), comment="封面图片")
    file_type = Column(String(10), comment="文件类型")
    file_url = Column(String(500), nullable=False, comment="文件URL")
    category = Column(String(20), comment="分类")
    task_status = Column(String(20), default="processing", comment="任务状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
    file_info = Column(JSON, comment="文件信息")

    # 关系
    course = relationship("Course", back_populates="lessons")
    cir_sections = relationship("CIRSection", back_populates="lesson")

    def __repr__(self):
        return f"<Lesson(id={self.lesson_id}, title={self.title})>"
