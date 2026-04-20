"""
课程与课件 Repository
处理 courses、lessons 表的读写操作
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

try:
    from backend.app.models.course import Course as CourseModel, Lesson
    from backend.app.models.course import CourseCategory
except ImportError:
    from app.models.course import Course as CourseModel, Lesson
    from app.models.course import CourseCategory

logger = logging.getLogger(__name__)


class CourseSystemRepository:
    """课程体系数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[CourseModel]:
        """获取所有课程"""
        try:
            return self.db.query(CourseModel).all()
        except Exception as e:
            logger.error(f"Failed to get courses: {e}")
            return []

    def get_by_id(self, course_id: str) -> Optional[CourseModel]:
        """根据ID获取课程"""
        try:
            return self.db.query(CourseModel).filter(
                CourseModel.course_id == course_id
            ).first()
        except Exception as e:
            logger.error(f"Failed to get course by id: {e}")
            return None

    def get_by_school(self, school_id: str) -> List[CourseModel]:
        """根据学校ID获取课程列表"""
        try:
            return self.db.query(CourseModel).filter(
                CourseModel.school_id == school_id
            ).all()
        except Exception as e:
            logger.error(f"Failed to get courses by school: {e}")
            return []

    def create(self, course_id: str, school_id: str, course_name: str, **kwargs) -> CourseModel:
        """创建课程"""
        try:
            course = CourseModel(
                course_id=course_id,
                school_id=school_id,
                course_name=course_name,
                **kwargs
            )
            self.db.add(course)
            self.db.commit()
            self.db.refresh(course)
            logger.info(f"Course created: course_id={course.course_id}")
            return course
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create course: {e}")
            raise

    def update(self, course_id: str, **kwargs) -> Optional[CourseModel]:
        """更新课程"""
        try:
            course = self.db.query(CourseModel).filter(
                CourseModel.course_id == course_id
            ).first()
            if not course:
                return None
            for key, value in kwargs.items():
                if hasattr(course, key):
                    setattr(course, key, value)
            self.db.commit()
            self.db.refresh(course)
            logger.info(f"Course updated: course_id={course_id}")
            return course
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update course: {e}")
            raise

    def delete(self, course_id: str) -> bool:
        """删除课程"""
        try:
            course = self.db.query(CourseModel).filter(
                CourseModel.course_id == course_id
            ).first()
            if not course:
                return False
            self.db.delete(course)
            self.db.commit()
            logger.info(f"Course deleted: course_id={course_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete course: {e}")
            raise


class LessonRepository:
    """课件数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, course_id: str = None) -> List[Lesson]:
        """获取课件列表（可选按课程过滤）"""
        try:
            query = self.db.query(Lesson)
            if course_id:
                query = query.filter(Lesson.course_id == course_id)
            return query.all()
        except Exception as e:
            logger.error(f"Failed to get lessons: {e}")
            return []

    def get_by_id(self, lesson_id: str) -> Optional[Lesson]:
        """根据ID获取课件"""
        try:
            return self.db.query(Lesson).filter(
                Lesson.lesson_id == lesson_id
            ).first()
        except Exception as e:
            logger.error(f"Failed to get lesson by id: {e}")
            return None

    def get_by_course(self, course_id: str) -> List[Lesson]:
        """根据课程ID获取课件列表"""
        try:
            return self.db.query(Lesson).filter(
                Lesson.course_id == course_id
            ).all()
        except Exception as e:
            logger.error(f"Failed to get lessons by course: {e}")
            return []

    def get_by_school(self, school_id: str) -> List[Lesson]:
        """根据学校ID获取课件列表"""
        try:
            return self.db.query(Lesson).filter(
                Lesson.school_id == school_id
            ).all()
        except Exception as e:
            logger.error(f"Failed to get lessons by school: {e}")
            return []

    def create(self, lesson_id: str, course_id: str, school_id: str, title: str, file_url: str, **kwargs) -> Lesson:
        """创建课件"""
        try:
            lesson = Lesson(
                lesson_id=lesson_id,
                course_id=course_id,
                school_id=school_id,
                title=title,
                file_url=file_url,
                **kwargs
            )
            self.db.add(lesson)
            self.db.commit()
            self.db.refresh(lesson)
            logger.info(f"Lesson created: lesson_id={lesson.lesson_id}")
            return lesson
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create lesson: {e}")
            raise

    def update(self, lesson_id: str, **kwargs) -> Optional[Lesson]:
        """更新课件"""
        try:
            lesson = self.db.query(Lesson).filter(
                Lesson.lesson_id == lesson_id
            ).first()
            if not lesson:
                return None
            for key, value in kwargs.items():
                if hasattr(lesson, key):
                    setattr(lesson, key, value)
            self.db.commit()
            self.db.refresh(lesson)
            logger.info(f"Lesson updated: lesson_id={lesson_id}")
            return lesson
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update lesson: {e}")
            raise

    def update_status(self, lesson_id: str, task_status: str) -> Optional[Lesson]:
        """更新课件任务状态"""
        try:
            lesson = self.db.query(Lesson).filter(
                Lesson.lesson_id == lesson_id
            ).first()
            if not lesson:
                return None
            lesson.task_status = task_status
            self.db.commit()
            self.db.refresh(lesson)
            logger.info(f"Lesson status updated: lesson_id={lesson_id}, status={task_status}")
            return lesson
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update lesson status: {e}")
            raise

    def delete(self, lesson_id: str) -> bool:
        """删除课件"""
        try:
            lesson = self.db.query(Lesson).filter(
                Lesson.lesson_id == lesson_id
            ).first()
            if not lesson:
                return False
            self.db.delete(lesson)
            self.db.commit()
            logger.info(f"Lesson deleted: lesson_id={lesson_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete lesson: {e}")
            raise


class CourseCategoryRepository:
    """课程分类数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[CourseCategory]:
        """获取所有分类"""
        try:
            return self.db.query(CourseCategory).order_by(
                CourseCategory.sort_order
            ).all()
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []

    def get_by_school(self, school_id: str) -> List[CourseCategory]:
        """根据学校ID获取分类列表"""
        try:
            return self.db.query(CourseCategory).filter(
                CourseCategory.school_id == school_id
            ).order_by(CourseCategory.sort_order).all()
        except Exception as e:
            logger.error(f"Failed to get categories by school: {e}")
            return []

    def create(self, school_id: str, category_name: str, sort_order: int = 0) -> CourseCategory:
        """创建分类"""
        try:
            category = CourseCategory(
                school_id=school_id,
                category_name=category_name,
                sort_order=sort_order
            )
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            logger.info(f"CourseCategory created: id={category.category_id}")
            return category
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create category: {e}")
            raise
